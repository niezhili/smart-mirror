from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
pic_path=Path(os.path.join(os.path.dirname(__file__),"pic"))
font_path=Path(os.path.join(os.path.dirname(__file__), '../common/calli/yanshi.ttf')).resolve()
mask_path=Path(os.path.join(os.path.dirname(__file__), 'mask.jpg')).resolve()
def compose_image_from_text(text, image_folder=pic_path, font_path=font_path, font_size=50,mask_path=mask_path):
    """
    根据输入文字生成拼接图片
    
    Args:
        text (str): 要拼接的文字内容
        image_folder (str): 图片库目录路径，默认为"save11"
        font_path (str): 字体文件路径，用于填充图片库中没有的字
        font_size (int): 字体大小，默认为50
    
    Returns:
        PIL.Image: 拼接后的图片对象
    
    Raises:
        ValueError: 当输入文字为空时抛出异常
    """
    if not text:
        raise ValueError("输入文字不能为空")

    if mask_path==None:
        mask_path=Path(__file__).parent / "mask.jpg"
    # 加载字符图片
    images = {}
    if os.path.exists(image_folder):
        # 加载所有图片文件
        image_files = [f for f in os.listdir(image_folder)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
        for filename in image_files:
            char_name = os.path.splitext(filename)[0]
            file_path = os.path.join(image_folder, filename)
            
            try:
                image = Image.open(file_path)
                images[char_name] = image
            except Exception as e:
                print(f"无法加载图片 {filename}: {e}")
    
    # 将文字按行分割（处理过长文本）
    lines = wrap_text(text, 7)  # 每行最多8个字符
    
    # 如果没有可用的字符图片，直接创建纯字体图片
    if not images:
        return create_font_based_image(text, font_path, font_size,mask_path=mask_path)
    
    # 计算每张图片的尺寸（以第一张图片为基准）
    sample_image = next(iter(images.values()))
    img_width, img_height = sample_image.size
    
    # 创建结果图片
    # 宽度 = 单张图片宽度 * 每行最大字符数
    # 高度 = 单张图片高度 * 行数
    result_width = img_width * max(len(line) for line in lines)
    result_height = img_height * len(lines)
    
    composed_image = Image.new('RGB', (result_width, result_height), (255, 255, 255))
    
    # 拼接每行文字
    for line_idx, line in enumerate(lines):
        for char_idx, char in enumerate(line):
            # 计算粘贴位置
            x_offset = char_idx * img_width
            y_offset = line_idx * img_height
            
            # 如果字符有对应的图片，则使用图片
            if char in images:
                char_image = images[char]
                composed_image.paste(char_image, (x_offset, y_offset))
            else:
                # 否则使用字体生成字符图片
                char_image = create_single_char_image(char, img_width, img_height, font_path, font_size,mask_path)
                composed_image.paste(char_image, (x_offset, y_offset))
    
    return composed_image


def wrap_text(text, max_chars_per_line):
    """
    简单文本换行处理
    
    Args:
        text (str): 需要换行处理的文本
        max_chars_per_line (int): 每行最大字符数
    
    Returns:
        list: 分行后的文本列表
    """
    lines = []
    current_line = ""
    
    for char in text:
        if len(current_line) >= max_chars_per_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line += char
    
    if current_line:
        lines.append(current_line)
    
    return lines


def create_single_char_image(char, width, height, font_path=None, font_size=50,mask_path=None):
    """
    创建单个字符的图片
    
    Args:
        char (str): 单个字符
        width (int): 图片宽度
        height (int): 图片高度
        font_path (str): 字体文件路径
        font_size (int): 字体大小
    
    Returns:
        PIL.Image: 字符图片
    """
    if mask_path==None:
        mask_path=Path(__file__).parent / "mask.jpg"
    try:
        image= Image.open(mask_path)
        image = image.resize((width, height))
    except Exception:
        image = Image.new('RGB', (width, height), (255, 255, 255))

    draw = ImageDraw.Draw(image)
    
    # 尝试使用指定字体，如果不可用则使用默认字体
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 计算文字位置使其居中
    try:
        bbox = draw.textbbox((0, 0), char, font=font)
    except Exception:
        bbox = (0, 0, width // 2, height // 2)
    
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文字
    draw.text((x, y-80), char, font=font, fill=(250, 250, 210))
    
    return image


def create_font_based_image(text, font_path=None, font_size=50,mask_path=None):
    """
    当没有图片库时，完全使用字体生成图片
    
    Args:
        text (str): 要生成的文字
        font_path (str): 字体文件路径
        font_size (int): 字体大小
    
    Returns:
        PIL.Image: 生成的图片

    """
    if mask_path==None:
        mask_path=Path(__file__).parent / "mask.jpg"

    lines = wrap_text(text, 8)
    
    # 创建足够大的画布
    char_width = font_size
    char_height = int(font_size * 1.5)
    
    width = char_width * max(len(line) for line in lines)
    height = char_height * len(lines)

    try:
        mask_image=Image.open(mask_path)
        mask_image=mask_image.resize((width,height))
        image=mask_image.convert("RGB")
    except Exception as e:
        print(f"无法加载图片 {mask_path}: {e}")
        image = Image.new('RGB', (width, height), (255, 255, 255))

    draw = ImageDraw.Draw(image)
    
    # 尝试使用指定字体
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 绘制每行文字
    for line_idx, line in enumerate(lines):
        for char_idx, char in enumerate(line):
            x = char_idx * char_width
            y = line_idx * char_height
            
            draw.text((x, y-80), char, font=font, fill=(250, 250, 210))
    
    return image


def main():
    """
    使用示例和测试函数
    """
    # 示例：使用图片库生成拼接图片
    image = compose_image_from_text(
        text="usdvguysgbaduoygweoyugdoy gweoygdhoy f大江东去撒vuv啊是绿茶丽萨办理的身份访，。，//，。，问英国完工于i的还好我还我一个单一哦我给i哦对工艺哦啊还是iu等你下班司法部微博反扑i我国覅偶遇跟iowg哦好7ioh佛给分工给",
        font_size=250
    )
    
    # 保存结果
    image.save("output_image.jpg")
    print("图片已保存为 output_image.jpg")
    
    # 显示图片（如果在有GUI的环境中）
    try:
        image.show()
    except Exception:
        print("无法显示图片，但已成功保存")


if __name__ == "__main__":
    main()