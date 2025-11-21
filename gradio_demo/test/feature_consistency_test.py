#!/usr/bin/env python3
"""
特征一致性验证脚本
验证HuggingFace和ModelScope上的相同CLIP模型提取特征的一致性
"""

import os
import numpy as np
import yaml
import tempfile
import shutil
from pathlib import Path
from image_master import ImageMaster


def create_test_configs():
    """创建测试用的配置文件"""
    
    # HuggingFace配置
    hf_config = {
        'model': {
            'source': 'huggingface',
            'name': 'openai/clip-vit-base-patch16',
            'name_modelscope': 'openai-mirror/clip-vit-base-patch16',
            'device': 'cpu'
        },
        'database': {
            'default_path': 'local_data/test_hf',
            'data_file': 'image_features.jsonl'
        },
        'similarity': {
            'threshold': 0.8,
            'max_results': 5
        },
        'image': {
            'max_size': [512, 512],
            'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        },
        'compression': {
            'feature_precision': 6,
            'encoding': 'base64'
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/test_hf.log'
        }
    }
    
    # ModelScope配置
    ms_config = hf_config.copy()
    ms_config['model']['source'] = 'modelscope'
    ms_config['database']['default_path'] = 'local_data/test_ms'
    ms_config['logging']['file'] = 'logs/test_ms.log'
    
    return hf_config, ms_config


def save_config(config, config_path):
    """保存配置到文件"""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def test_feature_consistency():
    """测试特征一致性"""
    
    print("🔬 开始特征一致性验证测试")
    print("=" * 60)
    
    # 创建临时配置文件
    hf_config, ms_config = create_test_configs()
    
    hf_config_path = "/tmp/hf_config.yaml"
    ms_config_path = "/tmp/ms_config.yaml"
    
    save_config(hf_config, hf_config_path)
    save_config(ms_config, ms_config_path)
    
    # 测试图片路径
    test_image = "/workspace/asset/test_img/cat_1.jpeg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    print(f"📷 测试图片: {test_image}")
    
    try:
        # 测试HuggingFace模型
        print("\n🤗 测试HuggingFace模型...")
        hf_im = ImageMaster()
        hf_im.set_from_config(hf_config_path)
        hf_im.init_model()
        
        print("✅ HuggingFace模型载入成功")
        hf_feature = hf_im.extract_feature(test_image)
        print(f"📊 HF特征维度: {hf_feature.shape}")
        print(f"📊 HF特征范围: [{hf_feature.min():.6f}, {hf_feature.max():.6f}]")
        print(f"📊 HF特征均值: {hf_feature.mean():.6f}")
        print(f"📊 HF特征标准差: {hf_feature.std():.6f}")
        
    except Exception as e:
        print(f"❌ HuggingFace模型测试失败: {e}")
        hf_feature = None
    
    try:
        # 测试ModelScope模型
        print("\n🏛️ 测试ModelScope模型...")
        ms_im = ImageMaster()
        ms_im.set_from_config(ms_config_path)
        ms_im.init_model()
        
        print("✅ ModelScope模型载入成功")
        ms_feature = ms_im.extract_feature(test_image)
        print(f"📊 MS特征维度: {ms_feature.shape}")
        print(f"📊 MS特征范围: [{ms_feature.min():.6f}, {ms_feature.max():.6f}]")
        print(f"📊 MS特征均值: {ms_feature.mean():.6f}")
        print(f"📊 MS特征标准差: {ms_feature.std():.6f}")
        
    except Exception as e:
        print(f"❌ ModelScope模型测试失败: {e}")
        ms_feature = None
    
    # 比较特征
    if hf_feature is not None and ms_feature is not None:
        print("\n🔍 特征一致性分析")
        print("-" * 40)
        
        # 计算差异
        diff = np.abs(hf_feature - ms_feature)
        max_diff = diff.max()
        mean_diff = diff.mean()
        
        # 计算余弦相似度
        from sklearn.metrics.pairwise import cosine_similarity
        cosine_sim = cosine_similarity([hf_feature], [ms_feature])[0][0]
        
        # 计算L2距离
        l2_distance = np.linalg.norm(hf_feature - ms_feature)
        
        print(f"📏 最大绝对差异: {max_diff:.8f}")
        print(f"📏 平均绝对差异: {mean_diff:.8f}")
        print(f"📏 余弦相似度: {cosine_sim:.8f}")
        print(f"📏 L2距离: {l2_distance:.8f}")
        
        # 判断一致性
        tolerance = 1e-6  # 容忍度
        
        print(f"\n🎯 一致性判断 (容忍度: {tolerance})")
        print("-" * 40)
        
        if max_diff < tolerance:
            print("✅ 特征完全一致 (在容忍度范围内)")
        elif cosine_sim > 0.999:
            print("✅ 特征高度一致 (余弦相似度 > 0.999)")
        elif cosine_sim > 0.99:
            print("⚠️ 特征基本一致 (余弦相似度 > 0.99)")
        else:
            print("❌ 特征存在显著差异")
        
        # 输出详细的差异分析
        print(f"\n📋 详细差异统计")
        print("-" * 40)
        percentiles = [50, 75, 90, 95, 99]
        for p in percentiles:
            print(f"第{p}百分位差异: {np.percentile(diff, p):.8f}")
    
    else:
        print("\n❌ 无法进行特征比较 (一个或两个模型加载失败)")
    
    # 清理临时文件
    for config_path in [hf_config_path, ms_config_path]:
        if os.path.exists(config_path):
            os.remove(config_path)
    
    print(f"\n🎉 特征一致性验证测试完成!")


def test_multiple_images():
    """对多张图片进行一致性测试"""
    
    print("\n" + "=" * 60)
    print("🖼️ 多图片特征一致性测试")
    print("=" * 60)
    
    test_images = [
        "/workspace/asset/test_img/cat_1.jpeg",
        "/workspace/asset/test_img/dog_1.jpg",
        "/workspace/asset/test_img/apple_1.jpg"
    ]
    
    # 创建配置
    hf_config, ms_config = create_test_configs()
    hf_config_path = "/tmp/hf_config_multi.yaml"
    ms_config_path = "/tmp/ms_config_multi.yaml"
    
    save_config(hf_config, hf_config_path)
    save_config(ms_config, ms_config_path)
    
    try:
        # 初始化两个模型
        print("🚀 初始化模型...")
        hf_im = ImageMaster()
        hf_im.set_from_config(hf_config_path)
        hf_im.init_model()
        
        ms_im = ImageMaster()
        ms_im.set_from_config(ms_config_path)
        ms_im.init_model()
        
        print("✅ 两个模型初始化完成")
        
        consistency_results = []
        
        for i, test_image in enumerate(test_images, 1):
            if not os.path.exists(test_image):
                print(f"⚠️ 跳过不存在的图片: {test_image}")
                continue
                
            print(f"\n📷 测试图片 {i}: {Path(test_image).name}")
            
            # 提取特征
            hf_feature = hf_im.extract_feature(test_image)
            ms_feature = ms_im.extract_feature(test_image)
            
            # 计算相似度
            from sklearn.metrics.pairwise import cosine_similarity
            cosine_sim = cosine_similarity([hf_feature], [ms_feature])[0][0]
            
            # 计算差异
            diff = np.abs(hf_feature - ms_feature)
            max_diff = diff.max()
            mean_diff = diff.mean()
            
            print(f"  余弦相似度: {cosine_sim:.8f}")
            print(f"  最大差异: {max_diff:.8f}")
            print(f"  平均差异: {mean_diff:.8f}")
            
            consistency_results.append({
                'image': Path(test_image).name,
                'cosine_similarity': cosine_sim,
                'max_diff': max_diff,
                'mean_diff': mean_diff
            })
        
        # 汇总结果
        print(f"\n📊 汇总结果")
        print("-" * 50)
        
        if consistency_results:
            avg_cosine = np.mean([r['cosine_similarity'] for r in consistency_results])
            avg_max_diff = np.mean([r['max_diff'] for r in consistency_results])
            avg_mean_diff = np.mean([r['mean_diff'] for r in consistency_results])
            
            print(f"平均余弦相似度: {avg_cosine:.8f}")
            print(f"平均最大差异: {avg_max_diff:.8f}")
            print(f"平均差异: {avg_mean_diff:.8f}")
            
            # 总体一致性判断
            if avg_cosine > 0.999:
                print("✅ 所有图片的特征都高度一致!")
            elif avg_cosine > 0.99:
                print("✅ 所有图片的特征基本一致")
            else:
                print("⚠️ 部分图片特征存在差异")
        
    except Exception as e:
        print(f"❌ 多图片测试失败: {e}")
    
    finally:
        # 清理临时文件
        for config_path in [hf_config_path, ms_config_path]:
            if os.path.exists(config_path):
                os.remove(config_path)


if __name__ == "__main__":
    test_feature_consistency()
    test_multiple_images()
