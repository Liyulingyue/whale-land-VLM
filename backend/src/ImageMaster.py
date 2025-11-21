import os
import json
import yaml
import base64
import logging
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Optional, Union
from sklearn.metrics.pairwise import cosine_similarity
from transformers import CLIPProcessor, CLIPModel
import torch

from tqdm import tqdm

class ImageMaster:
    """图像特征提取和相似度匹配类"""
    
    def __init__(self):
        self.config = None
        self.model = None
        self.processor = None
        self.database = []  # [{"feature": np.array, "name": str}, ...]
        self.database_path = None
        self.data_file_path = None
        self.logger = None
        
    def set_from_config(self, config_file_path: str):
        """从配置文件载入设置"""
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # 设置路径
            self.database_path = Path(self.config['database']['default_path'])
            self.data_file_path = self.database_path / self.config['database']['data_file']
            
            # 创建必要的目录
            self.database_path.mkdir(parents=True, exist_ok=True)
            Path(self.config['logging']['file']).parent.mkdir(parents=True, exist_ok=True)
            
            # 设置日志
            logging.basicConfig(
                level=getattr(logging, self.config['logging']['level']),
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(self.config['logging']['file'], encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
            self.logger.info("配置文件载入成功")
            
        except Exception as e:
            print(f"载入配置文件失败: {e}")
            raise

    def init_model(self):
        if self.config['backend'] == 'openvino':
            self._init_openvino_model()
        elif self.config['backend'] == 'huggingface':
            self._init_huggingface_model()
        else:
            raise ValueError(f"不支持的后端: {self.config['backend']}")

    def _init_openvino_model(self):
        import openvino as ov
        try:
            core = ov.Core()
            device = self.config['model']['device']
            model_name = self.config['model']['name']
            model_path = self.config['model']['path']
            force_download = self.config['model'].get('force_download', False)
            self.model = core.compile_model(model_path, device)
            self.processor = CLIPProcessor.from_pretrained(model_name, force_download=force_download)
        except Exception as e:
            self.logger.error(f"OpenVINO模型初始化失败: {e}")
            raise

    def _init_huggingface_model(self):
        """初始化CLIP模型"""
        try:
            device = self.config['model']['device']
            model_source = self.config['model'].get('source', 'huggingface')
            model_name = self.config['model']['name']
            
            # 设置HuggingFace镜像
            if model_source.lower() == 'hf_mirror':
                mirror_url = self.config['model'].get('mirror_url', 'https://hf-mirror.com')
                self.logger.info(f"正在从HF镜像载入模型: {model_name}, 镜像: {mirror_url}, 设备: {device}")
                
                # 设置环境变量使用镜像
                import os
                original_hf_endpoint = os.environ.get('HF_ENDPOINT')
                os.environ['HF_ENDPOINT'] = mirror_url
                
                try:
                    force_download = self.config['model'].get('force_download', False)
                    print(f"force_download: {force_download}")
                    self.model = CLIPModel.from_pretrained(model_name, force_download=force_download)
                    self.processor = CLIPProcessor.from_pretrained(model_name, force_download=force_download)
                    self.logger.info(f"成功从镜像站载入模型: {mirror_url}")
                except Exception as e:
                    self.logger.warning(f"镜像站加载失败: {e}，回退到官方HuggingFace")
                    # 恢复原始环境变量
                    if original_hf_endpoint:
                        os.environ['HF_ENDPOINT'] = original_hf_endpoint
                    else:
                        os.environ.pop('HF_ENDPOINT', None)
                    
                    # 回退到官方HuggingFace
                    force_download = self.config['model'].get('force_download', False)
                    print(f"force_download: {force_download}")
                    self.model = CLIPModel.from_pretrained(model_name, force_download=force_download)
                    self.processor = CLIPProcessor.from_pretrained(model_name, force_download=force_download)
                    
            else:
                # 使用官方HuggingFace
                self.logger.info(f"正在从官方HuggingFace载入模型: {model_name}, 设备: {device}")

                use_local = self.config['model'].get('use_local', False)
                print(f"use_local: {use_local}")
                
                try:
                    if use_local:
                        print("直接载入本地模型")
                        self.model = CLIPModel.from_pretrained(model_name, force_download=False, local_files_only=True)
                        self.processor = CLIPProcessor.from_pretrained(model_name, force_download=False, local_files_only=True)
                    else:
                        # 尝试强制下载
                        force_download = self.config['model'].get('force_download', False)
                        print(f"force_download: {force_download}")
                        self.model = CLIPModel.from_pretrained(model_name, force_download=force_download)
                        self.processor = CLIPProcessor.from_pretrained(model_name, force_download=force_download)
                except Exception as e:
                    self.logger.warning(f"从官方HuggingFace下载模型失败，尝试使用本地缓存: {e}")
                    # 尝试使用本地缓存
                    self.model = CLIPModel.from_pretrained(model_name, force_download=False)
                    self.processor = CLIPProcessor.from_pretrained(model_name, force_download=False)
            
            # 设置设备
            if device == "cpu":
                self.model = self.model.to("cpu")
            else:
                self.model = self.model.to(device)
            
            self.model.eval()  # 设置为评估模式
            self.logger.info(f"模型初始化成功，来源: {model_source}")
            
        except Exception as e:
            self.logger.error(f"模型初始化失败: {e}")
            raise
    
    def _encode_feature(self, feature: np.ndarray) -> str:
        """将特征向量编码为压缩字符串"""
        # 将特征转换为指定精度的浮点数
        precision = self.config['compression']['feature_precision']
        feature_rounded = np.round(feature, precision)
        
        # 转换为字节并编码
        feature_bytes = feature_rounded.astype(np.float32).tobytes()
        encoded = base64.b64encode(feature_bytes).decode('utf-8')
        return encoded
    
    def _decode_feature(self, encoded_feature: str) -> np.ndarray:
        """将编码字符串解码为特征向量"""
        feature_bytes = base64.b64decode(encoded_feature.encode('utf-8'))
        feature = np.frombuffer(feature_bytes, dtype=np.float32)
        return feature
    
    def extract_feature(self, image: Union[str, Image.Image]) -> np.ndarray:
        """提取图像特征"""
        try:
            # 处理输入图像
            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"图像文件不存在: {image}")
                pil_image = Image.open(image).convert('RGB')
            elif isinstance(image, Image.Image):
                pil_image = image.convert('RGB')
            else:
                raise ValueError("输入必须是图像路径字符串或PIL Image对象")
            
            # 调整图像大小（如果配置中有设置）
            if 'max_size' in self.config['image']:
                max_size = tuple(self.config['image']['max_size'])
                pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 使用CLIP处理器预处理图像
            inputs = self.processor(images=pil_image, return_tensors="pt")

            if self.config['backend'] == 'openvino':
                # OpenVINO模型需要转换为OpenVINO格式
                inputs = {k: v.cpu().numpy() for k, v in inputs.items()}
                image_features = self.model(inputs)[-1]
                image_features = image_features / np.linalg.norm(image_features, axis=-1, keepdims=True)  # 归一化特征
                feature = image_features.flatten()
            else:
                # 提取特征
                device = next(self.model.parameters()).device
                inputs = {k: v.to(device) for k, v in inputs.items()}
                with torch.no_grad():
                    image_features = self.model.get_image_features(**inputs)
                    # 归一化特征
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                feature = image_features.cpu().numpy().flatten()
            
            self.logger.debug(f"成功提取特征，维度: {feature.shape}")
            return feature
            
        except Exception as e:
            self.logger.error(f"特征提取失败: {e}")
            raise
    
    def load_database(self):
        """从数据文件载入特征数据库"""
        self.database = []
        
        if not self.data_file_path.exists():
            self.logger.info("数据文件不存在，将创建新的数据库")
            return
        
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.strip()
                        if not line:
                            continue
                        
                        data = json.loads(line)
                        feature = self._decode_feature(data['feature'])
                        name = data['name']
                        
                        self.database.append({
                            'name': name,
                            'feature': feature
                        })
                        
                    except Exception as e:
                        self.logger.warning(f"载入第{line_num}行数据失败: {e}")
                        continue
            
            self.logger.info(f"数据库载入完成，共载入 {len(self.database)} 条记录")
            
        except Exception as e:
            self.logger.error(f"载入数据库失败: {e}")
            raise
    
    def _save_to_database(self, feature: np.ndarray, name: str):
        """保存单条记录到数据库文件"""
        try:
            record = {
                'name': name,
                'feature': self._encode_feature(feature)
            }
            
            # 追加到文件
            with open(self.data_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            self.logger.debug(f"记录已保存: {name}")
            
        except Exception as e:
            self.logger.error(f"保存记录失败: {e}")
            raise
    
    def record(self, image: Union[str, Image.Image], name: str):
        """记录一张新图片到数据库"""
        try:
            # 提取特征
            feature = self.extract_feature(image)
            
            # 添加到内存数据库
            self.database.append({
                'name': name,
                'feature': feature
            })
            
            # 保存到文件
            self._save_to_database(feature, name)
            
            self.logger.info(f"成功记录图片: {name}")
            
        except Exception as e:
            self.logger.error(f"记录图片失败: {e}")
            raise
    
    def extract_item_from_feature(self, feature: np.ndarray) -> List[Dict]:
        """从特征中提取最相似的物品"""
        if not self.database:
            self.logger.warning("数据库为空")
            return []
        
        try:
            # 准备所有数据库特征
            db_features = np.array([item['feature'] for item in self.database])
            
            # 计算余弦相似度
            similarities = cosine_similarity([feature], db_features)[0]
            
            # 获取最相似的结果
            max_results = self.config['similarity']['max_results']
            top_indices = np.argsort(similarities)[::-1][:max_results]
            
            results = []
            for idx in top_indices:
                similarity = float(similarities[idx])
                name = self.database[idx]['name']
                
                results.append({
                    'name': name,
                    'similarity': similarity,
                    'index': int(idx)
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"特征匹配失败: {e}")
            raise
    
    def extract_item_from_image(self, image: Union[str, Image.Image]) -> List[Dict]:
        """从图片中提取物品"""
        try:
            feature = self.extract_feature(image)
            return self.extract_item_from_feature(feature)
        except Exception as e:
            self.logger.error(f"从图片提取物品失败: {e}")
            raise
    
    def _extract_name_from_filename(self, filename: str) -> str:
        """从文件名提取物品名"""
        # 移除文件扩展名
        name = Path(filename).stem
        
        # 如果包含下划线，移除最后一个下划线之后的内容
        if '_' in name:
            name = '_'.join(name.split('_')[:-1])
        
        return name
    
    def add_images(self, new_image_paths: Union[str, List[str]]):
        """从文件夹或文件列表批量添加图片"""
        if isinstance(new_image_paths, str):
            # 如果是目录路径，获取所有支持的图片文件
            image_dir = Path(new_image_paths)
            if not image_dir.exists():
                self.logger.error(f"目录不存在: {new_image_paths}")
                return
            
            supported_formats = self.config['image']['supported_formats']
            image_files = []
            for fmt in supported_formats:
                image_files.extend(image_dir.glob(f"*{fmt}"))
                # image_files.extend(image_dir.glob(f"*{fmt.upper()}"))
            
        else:
            # 如果是文件列表
            image_files = [Path(p) for p in new_image_paths]
        
        success_count = 0
        error_count = 0
        
        for image_path in tqdm(image_files, desc="添加图片"):
            try:
                # 提取物品名
                item_name = self._extract_name_from_filename(image_path.name)
                
                # 记录图片
                self.record(str(image_path), item_name)
                success_count += 1
                
                self.logger.info(f"成功添加: {image_path.name} -> {item_name}")
                
            except Exception as e:
                error_count += 1
                self.logger.warning(f"添加图片失败 {image_path.name}: {e}")
                continue
        
        self.logger.info(f"批量添加完成: 成功 {success_count} 张，失败 {error_count} 张")


# 使用示例和测试函数
def test_image_master():
    """测试ImageMaster类的功能"""
    # 初始化
    im = ImageMaster()

    # 定义路径
    base_dir = Path("C:/Users/Sirly/PycharmProjects/whale-land-VLM")
    db_file = base_dir / "official_image" / "image_features.jsonl"
    image_dir = base_dir / "base_image"
    
    
    # 载入配置
    config_path = base_dir  / "config" / "image_master.yaml"
    im.set_from_config(config_path)
    # 初始化模型
    print("正在初始化模型...")
    im.init_model()
    
    
    # 检查数据库文件和图片数量是否匹配
    rebuild_db = False
    
    if db_file.exists():
        # 计算数据库条目数
        with open(db_file, 'r', encoding='utf-8') as f:
            db_count = sum(1 for line in f if line.strip())
        
        # 计算图片数量
        supported_formats = im.config['image']['supported_formats']
        image_count = 0
        for fmt in supported_formats:
            image_count += len(list(image_dir.glob(f"*{fmt}")))
            # image_count += len(list(image_dir.glob(f"*{fmt.upper()}")))
        
        print(f"数据库条目数: {db_count}, 图片数量: {image_count}")
        
        if db_count != image_count:
            print("数据库条目数与图片数量不匹配，准备重新建库...")
            # 重命名原数据库文件
            backup_file = base_dir / "official_image" / "image_features_backup.jsonl"
            if backup_file.exists():
                backup_file.unlink()
            db_file.rename(backup_file)
            print(f"原数据库已备份至: {backup_file}")
            rebuild_db = True
    else:
        print("数据库文件不存在，准备建库...")
        rebuild_db = True
    
    # 重新建库
    if rebuild_db:
        print(f"开始从目录建库: {image_dir}")
        # 确保数据库目录存在
        db_dir = base_dir / "official_image"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # 清空内存数据库
        im.database = []
        # 如果数据文件已存在，删除它
        if db_file.exists():
            db_file.unlink()
        
        # 添加图片到数据库
        im.add_images(str(image_dir))
        print("建库完成")
    else:
        # 载入现有数据库
        print("数据库条目数与图片数量匹配，载入现有数据库...")
        im.load_database()
    
    # 测试搜索功能
    test_image = "../asset/images/烟头.jpg"
    if os.path.exists(test_image):
        print(f"\n使用测试图片: {test_image}")
        results = im.extract_item_from_image(test_image)
        if results:
            print("搜索结果:")
            for result in results:
                print(f"  匹配: {result['name']} (相似度: {result['similarity']:.4f})")
        else:
            print("未找到匹配结果")
    else:
        print(f"测试图片不存在: {test_image}")


if __name__ == "__main__":
    test_image_master()
