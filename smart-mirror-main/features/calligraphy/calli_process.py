from PIL import Image, ImageDraw, ImageFont
import os
from log.load_log import logger
from pathlib import Path

TAG = __name__
FONT_Path = Path(os.path.join(os.path.dirname(__file__), '../common/calli/yanshi.ttf')).resolve()


class Calli:
    def __init__(self):
        self.logger = logger.bind(tag=TAG)
        self.font_path = FONT_Path

    def create_vertical_calligraphy(self, raw_text, title="书法字帖", signature="——这是一个测试", font_size=60,
                                    columns=4, ):
        """
        创建竖排书法字帖（从右到左排列，类似青石板样式）

        Args:
            raw_text: 要书写的文字
            title: 标签名字
            font_size: 字体大小
            signature: 签名
            columns: 列数
        """
        # 保留所有字符包括标点和空格
        characters = list(raw_text)

        if not characters:
            print("没有找到有效的字符")
            return None

        # 计算尺寸
        char_spacing = int(font_size * 1.8)  # 字符间距
        column_spacing = int(font_size * 2.2)  # 列间距
        margin = int(font_size * 1.5)  # 边距
        # 计算图像尺寸
        # 每列的字符数
        chars_per_column = (len(characters) + columns - 1) // columns

        img_width = columns * column_spacing + 2 * margin
        img_height = chars_per_column * char_spacing + 2 * margin + 100  # 额外空间用于标题

        # 创建仿古风图像
        image_res = Image.new('RGB', (img_width, img_height), color=(245, 240, 230))  # 米黄色背景模拟青石板
        draw = ImageDraw.Draw(image_res)

        # 加载字体
        try:
            font = ImageFont.truetype(str(self.font_path), font_size)
            title_font = ImageFont.truetype(str(self.font_path), int(font_size * 0.8))
            signature_font = ImageFont.truetype(str(self.font_path), int(font_size * 0.6))
        except OSError:
            print("字体文件未找到，使用默认字体")
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            signature_font = ImageFont.load_default()
        # 绘制标题
        try:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
        except Exception as e:
            # 兼容旧版本Pillow
            title_bbox = (0, 0, font_size * 4, font_size)
            self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img_width - title_width) // 2
        draw.text((title_x, margin // 2), title, font=title_font, fill=(80, 60, 40))  # 深褐色文字

        # 绘制竖排文字（从右到左）
        for i, char in enumerate(characters):
            col = i // chars_per_column  # 列号
            row = i % chars_per_column  # 行号（从上到下）

            # 从右到左排列列
            column_index = columns - 1 - col

            # 计算字符位置
            x = margin + column_index * column_spacing + column_spacing // 2
            y = margin + row * char_spacing + 80  # 为标题留出空间

            # 绘制字符（居中）
            try:
                char_bbox = draw.textbbox((0, 0), char, font=font)
            except Exception as e:
                # 兼容旧版本Pillow
                char_bbox = (0, 0, font_size, font_size)
                self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

            char_width = char_bbox[2] - char_bbox[0]
            char_height = char_bbox[3] - char_bbox[1]

            char_x = x - char_width // 2
            char_y = y

            # 根据字符类型设置不同颜色
            if '\u4e00' <= char <= '\u9fff':  # 汉字
                fill_color = (20, 20, 20)  # 黑色
            elif char in '，。！？；：' or char in ',.!?;:':  # 标点符号
                fill_color = (40, 40, 40)  # 深灰色
            else:  # 其他字符
                fill_color = (60, 60, 60)  # 灰色

            draw.text((char_x, char_y), char, font=font, fill=fill_color)

        # 添加边框装饰
        border_margin = margin // 2
        draw.rectangle([border_margin, border_margin,
                        img_width - border_margin, img_height - border_margin],
                       outline=(120, 100, 80), width=3)  # 棕色边框

        # 添加签名栏

        try:
            signature_bbox = draw.textbbox((0, 0), signature, font=signature_font)
        except Exception as e:
            signature_bbox = (0, 0, font_size * 6, font_size // 2)
            self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

        signature_width = signature_bbox[2] - signature_bbox[0]
        signature_x = img_width - signature_width - margin
        signature_y = img_height - margin - 30
        draw.text((signature_x, signature_y), signature, font=signature_font, fill=(80, 60, 40))

        return image_res

    def create(self, raw_text, title="书法字帖", signature="——这是一个测试",
                                             font_size=60,choose="楷书"):
        """
        创建根据标点符号自动分行的竖排书法字帖
        每句话占一列，如果是绝句等可以分行的诗，则每半句占一列

        Args:
            raw_text: 要书写的文字
            title: 标签名字
            signature: 签名
            font_size: 字体大小
        """
        # 定义标点符号
        end_punctuation = '，。！？；：,.!?;:'

        # 分割句子
        segments = []
        current_segment = ""

        for char in raw_text:
            current_segment += char
            # 遇到逗号或句号等标点符号时分割
            if char in end_punctuation:
                segments.append(current_segment)
                current_segment = ""

        # 如果最后还有未结束的内容，也添加进去
        if current_segment:
            segments.append(current_segment)

        if not segments:
            print("没有找到有效的句子")
            return None

        # 计算尺寸
        char_spacing = int(font_size * 1.8)  # 字符间距
        column_spacing = int(font_size * 2.2)  # 列间距
        margin = int(font_size * 1.5)  # 边距

        # 计算最长句子的长度
        max_chars_per_column = max(len(segment) for segment in segments)

        # 计算图像尺寸
        columns = len(segments)
        img_width = columns * column_spacing + 2 * margin
        img_height = max_chars_per_column * char_spacing + 2 * margin + 100  # 额外空间用于标题

        # 创建仿古风图像
        image_res = Image.new('RGB', (img_width, img_height), color=(245, 240, 230))  # 米黄色背景模拟青石板
        draw = ImageDraw.Draw(image_res)

        # 加载字体
        try:
            font = ImageFont.truetype(str(self.font_path), font_size)
            title_font = ImageFont.truetype(str(self.font_path), int(font_size * 0.8))
            signature_font = ImageFont.truetype(str(self.font_path), int(font_size * 0.6))
        except OSError:
            print("字体文件未找到，使用默认字体")
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            signature_font = ImageFont.load_default()

        # 绘制标题
        try:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
        except Exception as e:
            # 兼容旧版本Pillow
            title_bbox = (0, 0, font_size * 4, font_size)
            self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img_width - title_width) // 2
        draw.text((title_x, margin // 2), title, font=title_font, fill=(80, 60, 40))  # 深褐色文字

        # 绘制竖排文字（从右到左）
        for col_idx, segment in enumerate(segments):
            for char_idx, char in enumerate(segment):
                # 从右到左排列列
                column_index = len(segments) - 1 - col_idx

                # 计算字符位置
                x = margin + column_index * column_spacing + column_spacing // 2
                y = margin + char_idx * char_spacing + 80  # 为标题留出空间

                # 绘制字符（居中）
                try:
                    char_bbox = draw.textbbox((0, 0), char, font=font)
                except Exception as e:
                    # 兼容旧版本Pillow
                    char_bbox = (0, 0, font_size, font_size)
                    self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

                char_width = char_bbox[2] - char_bbox[0]
                char_height = char_bbox[3] - char_bbox[1]

                char_x = x - char_width // 2
                char_y = y

                # 根据字符类型设置不同颜色
                if '\u4e00' <= char <= '\u9fff':  # 汉字
                    fill_color = (20, 20, 20)  # 黑色
                elif char in '，。！？；：' or char in ',.!?;:':  # 标点符号
                    fill_color = (40, 40, 40)  # 深灰色
                else:  # 其他字符
                    fill_color = (60, 60, 60)  # 灰色

                draw.text((char_x, char_y), char, font=font, fill=fill_color)

        # 添加边框装饰
        border_margin = margin // 2
        draw.rectangle([border_margin, border_margin,
                        img_width - border_margin, img_height - border_margin],
                       outline=(120, 100, 80), width=3)  # 棕色边框

        # 添加签名栏
        try:
            signature_bbox = draw.textbbox((0, 0), signature, font=signature_font)
        except Exception as e:
            signature_bbox = (0, 0, font_size * 6, font_size // 2)
            self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

        signature_width = signature_bbox[2] - signature_bbox[0]
        signature_x = img_width - signature_width - margin
        signature_y = img_height - margin - 30
        draw.text((signature_x, signature_y), signature, font=signature_font, fill=(80, 60, 40))

        return image_res


# 主程序
if __name__ == "__main__":
    # 加载字体（路径 + 字体大小）
    cali = Calli()
    # 要书写的文字（可以是古诗或其他文本）
    text = "枯藤老树昏鸦，小乔流水人家，古道西风瘦马，"

    # 创建竖排字帖
    image = cali.create_vertical_calligraphy(text,title="下",signature="-李白", font_size=60, columns=2)

    # 创建根据标点符号自动分行的竖排字帖
    image2 = cali.create_punctuation_based_calligraphy(text,title="静夜思",signature="-李白",  font_size=60)

    if image:
        # 保存图片
        image.save("1.png")
        # print("竖排字帖已保存为 calligraphy_output_vertical.png")
        image.show("1.png")

    if image2:
        # 保存图片
        image2.save("2.png")
        # print("根据标点符号自动分行的字帖已保存为 calligraphy_output_punctuation.png")
        image2.show("2.png")

    if not image and not image2:
        print("创建字帖失败")
