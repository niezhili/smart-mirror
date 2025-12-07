import argparse
import json
import sys
import time
from pathlib import Path
import hashlib
import getpass
from typing import Optional, Dict, Any

import cv2
import face_recognition
import numpy as np


def _has_gpu():
    try:
        return cv2.cuda.getCudaEnabledDeviceCount() > 0
    except Exception:
        return False


def _iter_image_paths(known_faces_dir: Path):
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.[jJ][pP][gG]", "*.[jJ][pP][eE][gG]", "*.[pP][nN][gG]"]
    for pat in patterns:
        for p in known_faces_dir.glob(pat):
            if p.is_file():
                yield p


def load_known_faces(known_faces_dir: Path):
    print(f"正在加载已知人脸：{known_faces_dir}")
    known_encodings = []
    known_names = []
    for person_dir in sorted(known_faces_dir.iterdir()):
        if not person_dir.is_dir():
            continue
        name = person_dir.name
        for image_path in _iter_image_paths(person_dir):
            image = cv2.imread(str(image_path))
            if image is None:
                continue
            h, w = image.shape[:2]
            if max(h, w) > 1024:
                scale = 1024 / max(h, w)
                image = cv2.resize(image, (int(w * scale), int(h * scale)))
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb, model="cnn" if _has_gpu() else "hog")
            encodings = face_recognition.face_encodings(rgb, locations)
            for enc in encodings:
                known_encodings.append(enc)
                known_names.append(name)
    print(f"已加载编码数：{len(known_encodings)}，共{len(set(known_names))}人")
    return known_encodings, known_names


def recognize_in_frame(frame, known_encodings, known_names, threshold: float = 0.6, scale: float = 0.5):
    results = []
    small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb, model="cnn" if _has_gpu() else "hog")
    encodings = face_recognition.face_encodings(rgb, locations)
    for (top, right, bottom, left), enc in zip(locations, encodings):
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=threshold)
        distances = face_recognition.face_distance(known_encodings, enc)
        name = "未知"
        confidence = 0.0
        matched = False
        if len(distances) > 0:
            idx = int(np.argmin(distances))
            confidence = float((1 - distances[idx]) * 100.0)
            if matches[idx]:
                name = known_names[idx]
                matched = True
        factor = 1.0 / scale if scale > 0 else 2.0
        results.append({
            "box": (int(top * factor), int(right * factor), int(bottom * factor), int(left * factor)),
            "name": name,
            "confidence": round(confidence, 1),
            "matched": matched,
        })
    return results


class AccountManager:
    """账号管理类"""

    def __init__(self, accounts_file: str = "accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = self.load_accounts()

    def load_accounts(self) -> Dict[str, Dict[str, Any]]:
        """从文件加载账号信息"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 创建默认账号文件
            default_accounts = {
                "admin": {
                    "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
                    "role": "admin",
                    "permissions": ["read", "write", "admin"]
                },
                "user1": {
                    "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
                    "role": "user",
                    "permissions": ["read"]
                }
            }
            self.save_accounts(default_accounts)
            return default_accounts
        except json.JSONDecodeError:
            print("账号文件格式错误，使用默认账号")
            return {}

    def save_accounts(self, accounts: Dict[str, Dict[str, Any]]):
        """保存账号信息到文件"""
        with open(self.accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)

    def add_account(self, username: str, password: str, role: str = "user", permissions: list = None):
        """添加新账号"""
        if permissions is None:
            permissions = ["read"]

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.accounts[username] = {
            "password_hash": password_hash,
            "role": role,
            "permissions": permissions
        }
        self.save_accounts(self.accounts)
        print(f"账号 {username} 已添加")

    def verify_login(self, username: str, password: str) -> bool:
        """验证登录"""
        if username not in self.accounts:
            return False

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.accounts[username]["password_hash"] == password_hash

    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.accounts.get(username)


class FaceLoginSystem:
    """人脸识别登录系统"""

    def __init__(self, known_faces_dir: Path, accounts_file: str = "accounts.json"):
        self.known_encodings, self.known_names = load_known_faces(known_faces_dir)
        self.account_manager = AccountManager(accounts_file)
        self.current_user = None
        self.login_time = None

    def recognize_and_login(self, webcam_index: int = 0, threshold: float = 0.6):
        """人脸识别并自动登录"""
        cap = cv2.VideoCapture(webcam_index)
        if not cap.isOpened():
            print("无法打开摄像头")
            return False

        print("请看向摄像头进行人脸识别登录...")
        print("按 'q' 键退出")

        success_count = 0
        max_success = 5  # 需要连续识别成功几次才算确认

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            results = recognize_in_frame(frame, self.known_encodings, self.known_names, threshold)

            # 在帧上绘制结果
            for result in results:
                top, right, bottom, left = result["box"]
                name = result["name"]
                confidence = result["confidence"]
                matched = result["matched"]

                # 设置颜色：匹配成功为绿色，未知为红色
                color = (0, 255, 0) if matched else (0, 0, 255)

                # 绘制人脸框
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                # 绘制标签
                label = f"{name} ({confidence:.1f}%)" if matched else "未知"
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # 如果识别成功，增加计数
                if matched:
                    success_count += 1
                    if success_count >= max_success:
                        # 执行登录
                        if self.perform_login(name):
                            print(f"人脸识别成功！用户 {name} 已登录")
                            cap.release()
                            cv2.destroyAllWindows()
                            return True
                else:
                    success_count = 0  # 重置计数

            # 显示帧
            cv2.imshow('人脸识别登录', frame)

            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return False

    def perform_login(self, username: str) -> bool:
        """执行登录操作"""
        # 检查账号是否存在
        if username not in self.account_manager.accounts:
            print(f"警告：未找到用户 {username} 的账号信息")
            print("您可以选择创建新账号或使用其他方式登录")
            return False

        # 获取用户信息
        user_info = self.account_manager.get_user_info(username)
        if not user_info:
            print(f"无法获取用户 {username} 的信息")
            return False

        # 设置当前用户
        self.current_user = username
        self.login_time = time.time()

        print(f"\n=== 登录成功 ===")
        print(f"用户：{username}")
        print(f"角色：{user_info['role']}")
        print(f"权限：{', '.join(user_info['permissions'])}")
        print(f"登录时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 20)

        return True

    def logout(self):
        """登出"""
        if self.current_user:
            print(f"用户 {self.current_user} 已登出")
            self.current_user = None
            self.login_time = None
        else:
            print("当前没有用户登录")

    def get_current_user(self) -> Optional[str]:
        """获取当前登录用户"""
        return self.current_user

    def get_user_permissions(self) -> list:
        """获取当前用户权限"""
        if self.current_user:
            user_info = self.account_manager.get_user_info(self.current_user)
            return user_info.get('permissions', []) if user_info else []
        return []

    def has_permission(self, required_permission: str) -> bool:
        """检查是否有特定权限"""
        return required_permission in self.get_user_permissions()


def main():
    #######################
    project_root = Path(__file__).parent.resolve()
    known_faces_dir = project_root / 'known_faces'
    #######################

    parser = argparse.ArgumentParser(description='人脸识别登录系统')
    parser.add_argument('--faces_dir', type=Path, default=Path('known_faces'),
                        help='已知人脸图片目录')
    parser.add_argument('--accounts_file', type=str, default='accounts.json',
                        help='账号信息文件')
    parser.add_argument('--threshold', type=float, default=0.6,
                        help='人脸识别阈值')
    parser.add_argument('--webcam', type=int, default=0,
                        help='摄像头索引')

    args = parser.parse_args()

    # 创建人脸识别登录系统
    face_login = FaceLoginSystem(args.faces_dir, args.accounts_file)

    print("人脸识别登录系统")
    print("1. 人脸识别登录")
    print("2. 手动登录")
    print("3. 添加账号")
    print("4. 退出")

    while True:
        choice = input("\n请选择操作 (1-4): ").strip()

        if choice == '1':
            # 人脸识别登录
            face_login.recognize_and_login(args.webcam, args.threshold)
            if face_login.get_current_user():
                break

        elif choice == '2':
            # 手动登录
            username = input("请输入用户名: ").strip()
            password = getpass.getpass("请输入密码: ")

            if face_login.account_manager.verify_login(username, password):
                face_login.current_user = username
                face_login.login_time = time.time()
                user_info = face_login.account_manager.get_user_info(username)

                print(f"\n=== 登录成功 ===")
                print(f"用户：{username}")
                print(f"角色：{user_info['role']}")
                print(f"权限：{', '.join(user_info['permissions'])}")
                print("=" * 20)
                break
            else:
                print("用户名或密码错误")

        elif choice == '3':
            # 添加账号
            username = input("请输入新用户名: ").strip()
            password = getpass.getpass("请输入密码: ")
            role = input("请输入角色 (默认user): ").strip() or "user"
            permissions_input = input("请输入权限 (用逗号分隔，默认read): ").strip()
            permissions = [p.strip() for p in permissions_input.split(',')] if permissions_input else ["read"]

            face_login.account_manager.add_account(username, password, role, permissions)

        elif choice == '4':
            print("退出系统")
            return

        else:
            print("无效选择，请重新输入")

    # 登录成功后，可以执行其他操作
    if face_login.get_current_user():
        print(f"\n欢迎，{face_login.get_current_user()}！")

        # 演示权限检查
        if face_login.has_permission("admin"):
            print("您具有管理员权限")
        elif face_login.has_permission("write"):
            print("您具有写入权限")
        else:
            print("您仅具有读取权限")

        input("\n按回车键退出...")


if __name__ == "__main__":
    main()