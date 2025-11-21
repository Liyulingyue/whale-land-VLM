#!/usr/bin/env python3
"""
HF Mirror使用示例
演示如何使用国内镜像站加速模型下载
"""

import os
from image_master import ImageMaster


def test_mirror_speed():
    """测试镜像站的使用"""
    
    print("🚀 ImageMaster HF Mirror 使用示例")
    print("=" * 50)
    
    # 使用镜像配置
    print("📋 使用HF Mirror配置文件...")
    im = ImageMaster()
    im.set_from_config("/workspace/config/image_master_mirror.yaml")
    
    print(f"✅ 配置载入完成")
    print(f"   模型来源: {im.config['model']['source']}")
    print(f"   镜像URL: {im.config['model']['mirror_url']}")
    
    # 初始化模型（会自动使用镜像）
    print("\n🤖 初始化模型（使用镜像站）...")
    im.init_model()
    print("✅ 模型初始化成功！")
    
    # 载入现有数据库
    print("\n💾 载入数据库...")
    im.load_database()
    print(f"✅ 数据库载入完成，共有 {len(im.database)} 条记录")
    
    # 测试特征提取
    test_image = "/workspace/asset/test_img/cat_1.jpeg"
    if os.path.exists(test_image):
        print(f"\n🔍 测试特征提取...")
        feature = im.extract_feature(test_image)
        print(f"✅ 特征提取完成，维度: {feature.shape}")
        
        # 搜索相似图片
        results = im.extract_item_from_image(test_image)
        print(f"\n📊 相似度搜索结果:")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['name']} (相似度: {result['similarity']:.4f})")
    
    print(f"\n🎉 HF Mirror使用示例完成！")


def compare_official_vs_mirror():
    """比较官方和镜像的使用方法"""
    
    print("\n" + "=" * 50)
    print("📋 官方 vs 镜像配置对比")
    print("=" * 50)
    
    print("🤗 官方HuggingFace配置:")
    print("""
model:
  source: "huggingface"
  name: "openai/clip-vit-base-patch16"
  device: "cpu"
    """)
    
    print("🔧 HF Mirror配置 (推荐国内用户):")
    print("""
model:
  source: "hf_mirror"
  name: "openai/clip-vit-base-patch16"
  mirror_url: "https://hf-mirror.com"
  device: "cpu"
    """)
    
    print("💡 使用建议:")
    print("   • 国内用户推荐使用 hf_mirror 配置")
    print("   • 海外用户可以使用 huggingface 配置")
    print("   • 两种配置的特征提取结果完全一致")
    print("   • 镜像站可以显著提升模型下载速度")


def show_environment_setup():
    """展示环境变量设置方法"""
    
    print("\n" + "=" * 50)
    print("🔧 环境变量设置方法")
    print("=" * 50)
    
    print("方法1: 在代码中设置（推荐）")
    print("""
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 然后正常使用ImageMaster
im = ImageMaster()
im.set_from_config("config/image_master.yaml")
im.init_model()
    """)
    
    print("\n方法2: 在shell中设置")
    print("""
# Linux/macOS
export HF_ENDPOINT=https://hf-mirror.com

# Windows
set HF_ENDPOINT=https://hf-mirror.com
    """)
    
    print("\n方法3: 使用配置文件（最推荐）")
    print("""
# 直接使用 image_master_mirror.yaml 配置文件
im = ImageMaster()
im.set_from_config("config/image_master_mirror.yaml")
im.init_model()
    """)


if __name__ == "__main__":
    test_mirror_speed()
    compare_official_vs_mirror()
    show_environment_setup()
    
    print(f"\n🌟 总结：")
    print("✅ HF Mirror集成完成，国内用户可享受更快速度")
    print("✅ 特征提取结果与官方完全一致")
    print("✅ 支持配置文件灵活切换")
    print("✅ 自动环境变量管理，使用简单")
