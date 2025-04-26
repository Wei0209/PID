import rclpy
import math
import random
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class TurtlePControl(Node):
    def __init__(self):
        super().__init__('turtle_p_control')

        # 訂閱烏龜的位置信息
        self.pose_subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        # 發布速度指令
        self.velocity_publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 生成第一個隨機目標點
        self.generate_new_target()

        # P 控制器增益
        self.Kp_angular = 2.0  # 角速度增益
        self.pose = None  # 當前烏龜位置
        self.timer = self.create_timer(1/30, self.control_loop)  # 33ms 週期執行

    def generate_new_target(self):
        """隨機生成新的目標點"""
        self.target_x = random.uniform(1.0, 10.0)
        self.target_y = random.uniform(1.0, 10.0)
        self.get_logger().info(f'新目標點: ({self.target_x:.2f}, {self.target_y:.2f})')

    def pose_callback(self, msg):
        """更新烏龜的當前位姿"""
        self.pose = msg

    def control_loop(self):
        """主控制迴圈"""
        if self.pose is None:
            return

        # 計算烏龜與目標點的角度誤差
        target_angle = math.atan2(self.target_y - self.pose.y, self.target_x - self.pose.x)
        error_theta = target_angle - self.pose.theta


        # 讓角度誤差保持在 -pi 到 pi 之間
        error_theta = math.atan2(math.sin(error_theta), math.cos(error_theta))

        # P 控制計算角速度
        angular_velocity = self.Kp_angular * error_theta

        # 限制最大角速度
        max_angular_speed = 2.0
        cmd_vel = Twist()
        cmd_vel.linear.x = 0.0
        cmd_vel.angular.z = max(-max_angular_speed, min(angular_velocity, max_angular_speed))
        
        self.velocity_publisher.publish(cmd_vel)

        # 顯示當前狀態
        self.get_logger().info(f'目標角度: {target_angle:.2f}, 當前角度: {self.pose.theta:.2f}, 角速度: {cmd_vel.angular.z:.2f}')

        # 如果角度誤差很小，表示烏龜已對準目標，生成新的目標點
        if abs(error_theta) < 0.05:
            self.get_logger().info('對準目標，生成新目標點')
            self.generate_new_target()

def main(args=None):
    rclpy.init(args=args)
    node = TurtlePControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()