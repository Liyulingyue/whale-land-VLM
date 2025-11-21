#!/usr/bin/env python3
"""
ImageMaster使用示例
演示如何使用ImageMaster类进行图像特征提取和相似度匹配
"""

import sys
import os

# 在这里修正帮助我找到ImageMaster
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置PROXY和PROXYS为8234
# os.environ['HTTP_PROXY'] = 'http://localhost:8234'
# os.environ['HTTPS_PROXY'] = 'http://localhost:8234'

from pathlib import Path
from src.ImageMaster import ImageMaster


def main():
    """主函数：演示ImageMaster的完整使用流程"""
    
    print("🚀 ImageMaster 使用示例")
    print("=" * 50)
    
    # 1. 初始化ImageMaster
    print("\n📋 步骤1: 初始化ImageMaster")
    im = ImageMaster()
    
    # 2. 载入配置文件
    print("\n⚙️ 步骤2: 载入配置文件")
    config_path = "config/image_master.yaml"
    im.set_from_config(config_path)
    print(f"✅ 配置文件载入完成: {config_path}")
    
    # 3. 初始化模型
    print("\n🤖 步骤3: 初始化CLIP模型")
    im.init_model()
    print("✅ 模型初始化完成")
    
    # 4. 载入现有数据库
    print("\n💾 步骤4: 载入现有数据库")
    im.load_database()
    print(f"✅ 数据库载入完成，共有 {len(im.database)} 条记录")
    
    # 5. 演示单张图片记录
    print("\n📷 步骤5: 记录新图片（示例）")
    # 这里只是演示，不实际执行，因为测试图片已经添加过了
    print("示例代码: im.record('/path/to/image.jpg', '物品名称')")
    
    # 6. 演示批量添加图片
    print("\n📁 步骤6: 批量添加图片（示例）")
    print("示例代码: im.add_images('/path/to/image/directory')")
    
    # 7. 演示相似度搜索
    print("\n🔍 步骤7: 演示相似度搜索")
    test_images = [
        "asset/test_img/cat_1.jpeg",
        "asset/test_img/dog_1.jpg",
        "asset/test_img/apple_1.jpg"
    ]
    
    for test_img_path in test_images:
        if os.path.exists(test_img_path):
            print(f"\n🖼️ 测试图片: {Path(test_img_path).name}")
            
            # 方法1: 直接从图片搜索
            results = im.extract_item_from_image(test_img_path)
            
            print("  🎯 最相似的物品:")
            for i, result in enumerate(results[:3], 1):  # 只显示前3个结果
                similarity_percent = result['similarity'] * 100
                print(f"    {i}. {result['name']} (相似度: {similarity_percent:.2f}%)")
                
                # 高相似度的判断
                if result['similarity'] > 0.9:
                    print(f"      ⭐ 高度匹配!")
                elif result['similarity'] > 0.8:
                    print(f"      ✅ 很相似")
                elif result['similarity'] > 0.7:
                    print(f"      ⚠️ 中等相似")
    
    # 8. 演示特征提取
    print("\n🧮 步骤8: 演示特征提取")
    if os.path.exists("asset/test_img/cat_1.jpeg"):
        feature = im.extract_feature("asset/test_img/cat_1.jpeg")
        print(f"✅ 特征提取完成，维度: {feature.shape}")
        
        # 从特征搜索
        print("🔍 使用提取的特征进行搜索:")
        results = im.extract_item_from_feature(feature)
        for result in results[:2]:
            print(f"  - {result['name']} (相似度: {result['similarity']:.4f})")
    
    # 9. 数据库统计
    print("\n📊 步骤9: 数据库统计信息")
    print(f"总记录数: {len(im.database)}")
    
    # 统计每个物品的数量
    name_counts = {}
    for item in im.database:
        name = item['name']
        name_counts[name] = name_counts.get(name, 0) + 1
    
    print("物品分布:")
    for name, count in sorted(name_counts.items()):
        print(f"  - {name}: {count} 张")
    
    print("\n🎉 示例演示完成!")
    print("\n💡 使用提示:")
    print("1. 相似度阈值可以在配置文件中调整")
    print("2. 支持的图片格式: .jpg, .jpeg, .png, .bmp, .tiff")
    print("3. 文件命名规则: 物品名.jpg 或 物品名_描述.jpg")
    print("4. 数据自动保存到 local_data/official_image/image_features.jsonl")


def demonstrate_api_usage():
    """演示API的详细使用方法"""
    
    print("\n" + "=" * 60)
    print("📚 ImageMaster API 详细使用说明")
    print("=" * 60)
    
    # 展示主要方法
    methods = [
        {
            "name": "set_from_config(config_file_path)",
            "description": "从YAML配置文件载入设置",
            "example": "im.set_from_config('config/image_master.yaml')"
        },
        {
            "name": "init_model()",
            "description": "初始化CLIP模型",
            "example": "im.init_model()"
        },
        {
            "name": "extract_feature(image)",
            "description": "提取图像特征向量",
            "example": "feature = im.extract_feature('path/to/image.jpg')"
        },
        {
            "name": "load_database()",
            "description": "从jsonl文件载入特征数据库",
            "example": "im.load_database()"
        },
        {
            "name": "record(image, name)",
            "description": "记录新图片到数据库",
            "example": "im.record('cat.jpg', '猫')"
        },
        {
            "name": "extract_item_from_image(image)",
            "description": "从图片中识别最相似的物品",
            "example": "results = im.extract_item_from_image('test.jpg')"
        },
        {
            "name": "extract_item_from_feature(feature)",
            "description": "从特征向量中识别最相似的物品",
            "example": "results = im.extract_item_from_feature(feature_vector)"
        },
        {
            "name": "add_images(new_image_paths)",
            "description": "批量添加图片（目录或文件列表）",
            "example": "im.add_images('images_folder/')"
        }
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n{i}. {method['name']}")
        print(f"   📝 {method['description']}")
        print(f"   💻 示例: {method['example']}")
    
    print("\n" + "=" * 60)
    print("🔧 配置文件说明 (config/image_master.yaml)")
    print("=" * 60)
    
    config_sections = [
        {
            "section": "model",
            "description": "模型设置",
            "items": ["name: CLIP模型名称", "device: 运行设备(cpu/cuda)"]
        },
        {
            "section": "database", 
            "description": "数据库设置",
            "items": ["default_path: 数据存储路径", "data_file: jsonl文件名"]
        },
        {
            "section": "similarity",
            "description": "相似度设置", 
            "items": ["threshold: 相似度阈值", "max_results: 返回结果数量"]
        },
        {
            "section": "image",
            "description": "图片处理设置",
            "items": ["max_size: 最大尺寸", "supported_formats: 支持格式"]
        }
    ]
    
    for section in config_sections:
        print(f"\n📂 {section['section']}: {section['description']}")
        for item in section['items']:
            print(f"   • {item}")


if __name__ == "__main__":
    main()
    # demonstrate_api_usage()
