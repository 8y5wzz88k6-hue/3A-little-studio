# 潮汐环线 · TIDELINE

一条穿过原创港区的 893.4 米夜间计时赛道，使用 Godot 4.7.2 Forward+ 制作。汐街商区以竖式灯箱、唱片店和夜市橱窗构成起跑直道。线路随后升至约 8.5 米的高架段，穿过轨道支架，再沿铸造厂的蒸汽管线下降，绕过末段弯道回到起点。

## 开始驾驶

在制作此项目的 Windows 电脑上双击 **启动赛道.cmd**。也可以在 Godot 项目管理器中导入 **project.godot**，按 **F6** 运行打开的主场景，或按 **F5** 直接运行项目。转移项目时保留整个文件夹，首次打开需要等待 Godot 导入素材。

| 按键 | 操作 |
| --- | --- |
| W / ↑ | 加速 |
| S / ↓ | 制动，停稳后倒车 |
| A、D / ←、→ | 转向 |
| 空格 | 手刹 |
| C | 切换追尾视角和左侧驾驶座视角。座舱内可查看实时后视镜、车速、挡位和中控导航。 |
| R | 在当前路段扶正车辆 |
| P / Esc | 暂停或继续 |
| H | 操作说明 |
| M | 引擎静音 |

首次踩下油门或制动时开始计时。顺序通过三个分段并越过起点后结算圈速，继续行驶可挑战个人最佳。最佳圈速保存在当前用户的 Godot 数据目录。

## 场景与素材

- **scenes/circuit.tscn** 是主场景，包含街区实例、环境光、车辆、相机和仪表。
- **scenes/harbor.scn** 是可在 Godot 编辑器中打开的街区场景。沿线建筑、道路、空中廊桥、轨道和管廊以命名节点分组。
- **source/blender/Kestrel_R9.blend** 是跑车的 Blender 源文件。**assets/Kestrel_R9.glb** 是运行模型，包含车身及四个独立的车轮。
- **assets/signs** 包含霓虹字牌、原创广告和店铺内景。**assets/harbor_radiance.exr** 从街道中央拍摄并烘焙，为清漆、玻璃与金属提供环境反光。路面积水使用随主相机移动的镜像视口。
- **preview/night_drive.mp4** 是穿过三个赛段的 12 秒实机录像。**preview/before_after.jpg** 并排展示相同机位下的车身与街景。**preview/route.png** 标出了赛道走向、检查点与路面高程。

## 重新生成

项目中已包含烘焙完成的场景和跑车。若要修改生成规则，先用带 Pillow 的 Python 运行 **source/art.py**，然后运行 **source/build_district.py** 生成几何数据和路线采样。用 Godot 的 **--headless --editor --import** 导入素材后，在项目目录执行 **godot --headless --script res://source/bake.gd** 重新保存街区。建模脚本 **source/blender/build_car.py** 可通过 Blender 的 **--background --python** 参数运行。招贴生成脚本使用 Windows 字体。

调整街区灯光后，可用 **godot --script res://source/bake_radiance.gd** 重新拍摄 HDR 光照全景。在 Godot 编辑器重新导入 EXR 后，车漆和玻璃会使用新的环境反光。
