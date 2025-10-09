from PIL import Image, ImageDraw, ImageFont
import os
from features.calligraphy.pintu import compose_image_from_text
from log.load_log import logger
from pathlib import Path
import re

TAG = __name__
FONT_Path_kaishu = Path(os.path.join(os.path.dirname(__file__), '../common/calli/yanshi.ttf')).resolve()
FONT_Path_pinyin = Path(os.path.join(os.path.dirname(__file__), '../common/calli/pinyin.ttf')).resolve()
FONT_Path_jinwen = Path(os.path.join(os.path.dirname(__file__), '../common/calli/jinwen.ttf')).resolve()
FONT_Path_heti = Path(os.path.join(os.path.dirname(__file__), '../common/calli/heti.ttf')).resolve()
FONT_Path_xingshu = Path(os.path.join(os.path.dirname(__file__), '../common/calli/xingshu.ttf')).resolve()


Muban_path=Path(os.path.join(os.path.dirname(__file__), 'muban.jpg')).resolve()


class Calli:
    def __init__(self):
        self.logger = logger.bind(tag=TAG)
        self.style={'楷书': FONT_Path_kaishu,'拼音':FONT_Path_pinyin,'金文':FONT_Path_jinwen,'鹤体':FONT_Path_heti,'行书':FONT_Path_xingshu}
        self.Muban_path=Muban_path

    def create(self, raw_text, title="书法字帖", signature="——佚名",
                                             font_size=60,choose="楷书"):


        font_path=self.style.get(choose,FONT_Path_kaishu)
        end_punctuation = '，。！？；：,.!?;:'
        segments = []
        current_segment = ""

        for char in raw_text:
            current_segment += char
            if char in end_punctuation:
                segments.append(current_segment)
                current_segment = ""

        if current_segment:
            segments.append(current_segment)

        if not segments:
            print("没有找到有效的句子")
            return None

        char_spacing = int(font_size * 1.8)
        column_spacing = int(font_size * 2.2)
        margin = int(font_size * 1.5)
        max_chars_per_column = max(len(segment) for segment in segments)

        columns = len(segments)
        img_width = columns * column_spacing + 2 * margin
        img_height = max_chars_per_column * char_spacing + 2 * margin + 100

        image_res = Image.new('RGB', (img_width, img_height), color=(245, 240, 230))
        draw = ImageDraw.Draw(image_res)
        try:
            font = ImageFont.truetype(str(font_path), font_size)
            title_font = ImageFont.truetype(str(font_path), int(font_size * 0.8))
            signature_font = ImageFont.truetype(str(font_path), int(font_size * 0.6))
        except OSError:
            print("字体文件未找到，使用默认字体")
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            signature_font = ImageFont.load_default()

        # 绘制标题
        try:
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
        except Exception as e:
            title_bbox = (0, 0, font_size * 4, font_size)
            self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

        title_width = title_bbox[2] - title_bbox[0]
        title_x = (img_width - title_width) // 2
        draw.text((title_x, margin // 2), title, font=title_font, fill=(80, 60, 40))

        for col_idx, segment in enumerate(segments):
            for char_idx, char in enumerate(segment):
                column_index = len(segments) - 1 - col_idx

                x = margin + column_index * column_spacing + column_spacing // 2
                y = margin + char_idx * char_spacing + 80

                try:
                    char_bbox = draw.textbbox((0, 0), char, font=font)
                except Exception as e:
                    char_bbox = (0, 0, font_size, font_size)
                    self.logger.warning(f"字体文件未找到，使用默认字体:{e}")

                char_width = char_bbox[2] - char_bbox[0]
                char_height = char_bbox[3] - char_bbox[1]

                char_x = x - char_width // 2
                char_y = y

                if '\u4e00' <= char <= '\u9fff':
                    fill_color = (20, 20, 20)
                elif char in '，。！？；：' or char in ',.!?;:':
                    fill_color = (40, 40, 40)
                else:
                    fill_color = (60, 60, 60)

                draw.text((char_x, char_y), char, font=font, fill=fill_color)

        border_margin = margin // 2
        draw.rectangle([border_margin, border_margin,
                        img_width - border_margin, img_height - border_margin],
                       outline=(120, 100, 80), width=3)
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

    def create_zitie(self, text, gold_color=(255, 250, 210), shadow_color=(139, 87, 42), font_size=88,choose="楷书"):
        """
        在模板 muban.jpg 上生成烫金书法字帖，文字写在中部黑色石板区域，每列不超过6个字，从右往左书写

        Args:
            text (str): 要书写的汉字文本
            gold_color (tuple): 烫金颜色，默认为金色 (255, 215, 0)
            shadow_color (tuple): 阴影颜色，模拟金属光泽，默认深棕
            font_size (int): 字体大小

        Returns:
            list: 包含PIL.Image对象的列表，每个对象代表一张图片
        """
        # 加载模板图像
        # 去标点
        font_path = self.style.get(choose, FONT_Path_kaishu)
        text = re.sub('[，。！？；：,.!?;:]', '', text)

        template_path = self.Muban_path
        if not template_path.exists():
            raise FileNotFoundError(f"模板文件未找到: {template_path}")

        image = Image.open(template_path).convert('RGB')
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype(str(font_path), font_size)
        except OSError:
            self.logger.warning("字体文件未找到，使用默认字体")
            font = ImageFont.load_default()

        # 黑色石板区域位置
        r1 = (988, 225, 900, 800)
        r2 = (779, 225, 900, 800)
        r3 = (570, 225, 900, 800)
        l1 = (470, 210, 520, 800)
        l2 = (275, 210, 520, 800)
        l3 = (57, 210, 520, 800)

        # 定义石板区域顺序
        boards = [r1, r2, r3, l1, l2, l3]

        # 分割文本为多列，每列最多6个字
        max_chars_per_col = 6
        cols = []
        current_col = []

        for char in text:
            if len(current_col) < max_chars_per_col:
                current_col.append(char)
            else:
                cols.append(current_col)
                current_col = [char]
        if current_col:
            cols.append(current_col)

        # 创建结果图片列表
        images = []
        current_col_index = 0

        # 当还有列未处理时继续
        while current_col_index < len(cols):
            # 加载新的模板图像
            image = Image.open(template_path).convert('RGB')
            draw = ImageDraw.Draw(image)

            # 在当前图片上绘制尽可能多的列（最多6列）
            for board_index in range(len(boards)):
                if current_col_index < len(cols):
                    col_text = ''.join(cols[current_col_index])
                    self._draw_gold_text(draw, col_text, boards[board_index], font, gold_color, shadow_color)
                    current_col_index += 1
                else:
                    break

            # 添加当前图片到结果列表
            images.append(image)

        return images

    def _draw_gold_text(self, draw, text, board_rect, font, gold_color, shadow_color):
        """
        在指定区域绘制烫金文字（带阴影）

        Args:
            draw: ImageDraw 对象
            text: 文本
            board_rect: 石板区域 (x1, y1, x2, y2)
            font: 字体对象
            gold_color: 金色
            shadow_color: 阴影色
        """
        x1, y1, x2, y2 = board_rect
        width = x2 - x1
        height = y2 - y1

        # 计算字符高度和行间距
        bbox = draw.textbbox((0, 0), text, font=font)
        char_height = bbox[3] - bbox[1]
        # print(char_height)
        line_spacing = int(76 * 1.3)

        # 从右往左书写，逐行排列
        lines = [text[i:i + 1] for i in range(0, len(text))]
        for i, char in enumerate(lines):
            # 每个字符居中对齐
            char_bbox = draw.textbbox((0, 0), char, font=font)
            char_width = char_bbox[2] - char_bbox[0]

            # 计算位置：水平居中，垂直从上往下
            x = x1 + (width - char_width) // 2
            y = y1 + i * line_spacing + (char_height // 2)

            # 绘制阴影（偏移量）
            draw.text((x + 1, y + 1), char, font=font, fill=shadow_color)
            # 绘制金色文字
            draw.text((x, y), char, font=font, fill=gold_color)



def ca():
    calli = Calli()
    result = calli.create_zitie('''大江东去，浪淘尽，千古风流人物。故垒西边，人道是，三国周郎赤壁。''', font_size=88)
    if result:
        for r in result:
            r.show()
            r.save("zitie_gold.png")
            print("烫金字帖已生成！")
if __name__ == "__main__":
    ca()

