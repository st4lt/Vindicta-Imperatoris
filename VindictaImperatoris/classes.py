from ursina import *
from direct.actor.Actor import Actor
from ursina.shaders import basic_lighting_shader, unlit_shader
from random import randint
from ursina.prefabs.health_bar import HealthBar
import time

custom_font = 'fonts/antikytheralaser.ttf'
game_is_paused = True 

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(collider='box', speed=35, color=color.white,
                         jump_height=0.5, texture='white_cube', position=(0, 0.2, 0), hp_player=100, shader=basic_lighting_shader, **kwargs)
        self.visual =self.visual = loader.loadModel("assets/humen_6.glb")
        self.visual.reparentTo(self) 
        self.mouse_sensitivity = 50
        camera.reparent_to(self)
        self.on_ground = False


        self.default_cam_pos = Vec3(2, 12, -10)
        self.default_cam_rot = Vec3(20, 0, 0)

        self.combat_cam_pos = Vec3(5, 5, -5)
        self.combat_cam_rot = Vec3(10, -90, 0)
        self.in_combat_view = False

        camera.position = self.default_cam_pos
        camera.rotation_x = self.default_cam_rot.x
        camera.fov = 120
        
        self.phb = HealthBar(
                   value = 100,
                   roundness = 0.25, 
                   highlight_color = color.black66, 
                   show_text = True, 
                   show_lines = False, 
                   text_size = 0.7, 
                   scale = (0.5, 0.025), 
                   origin = (-0.5, 0.5), 
                   name ='health_bar'
                   )

    def input(self, key):
        if key == 'scroll up':
            camera.z -= 1
        if key == 'scroll down':
            camera.z += 1

    def update(self):
        self.phb.enabled = not game_is_paused
        if game_is_paused:
            return
        direction = Vec3(self.forward * (held_keys['w'] - held_keys['s']) +
                     self.right * (held_keys['d'] - held_keys['a'])).normalized()
        self.position += direction * self.speed * time.dt
        self.rotation_y += mouse.velocity.x * self.mouse_sensitivity
        camera.rotation_x -= mouse.velocity.y * self.mouse_sensitivity
        camera.rotation_x = clamp(camera.rotation_x, -40, 40)


class Npc(Entity):
    def __init__(self, target, speed=15, **kwargs):
        super().__init__(model='humen_6.glb', collider='box',
                         color=color.gray, texture='white_cube', hp_npc=100, shader=basic_lighting_shader, **kwargs)
        self.target = target
        self.speed = 0
        self.base_speed = speed
        self.can_move = False
        self.velocity_y = 0
        self.gravity = 0.8
        self.can_attack = True
        invoke(self.enable_movement, delay=2)
        
        self.nhb = HealthBar(
                   value = 100,
                   bar_color=color.red.tint(-0.2),
                   highlight_color=color.black66, 
                   show_text=False,
                   parent = self,
                   y = 9,
                   scale = (1.5, 0.2),
                   billboard = True,
                   shader=unlit_shader,
                   )

    def enable_movement(self):
        self.speed = self.base_speed

    def update(self):
        if game_is_paused or not self.target:
            return
        self.look_at(self.target.position)
        distance = distance_xz(self.position, self.target.position)
        follow_distance = 3
        if distance > follow_distance:
            self.position += self.forward * self.speed * time.dt


class MainMenu(Entity):
    def __init__(self, on_restart_call, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.first_run = True 
        self.on_restart_call = on_restart_call
        self.create_buttons()
        self.create_title()
        self.show_menu()

    def create_title(self):
        self.title_bg = Entity(
            parent=camera.ui,
            model='quad',
            texture='assets/bg_title',
            origin=(0,0),
            scale=(1, 0.15),
            position=(0, 0.25))

        self.title = Text(text="VINDICTA IMPERATORIS",
            parent=self,
            scale=3,
            color=color.black,
            origin=(0,0),
            position=(0, 0.24),
            font=custom_font)

        self.story = Text(
            text="105 год до нашей эры. Коммод, император Великой Римской Империи, узнаёт о том, что его друг,\nгенерал  его собственной армии,великий воин Ферокс Викториан имел взаимные чувства с его женой Октавией.\nВ порыве гнева император, желая устроить показательную смерть,\nунижение предателя, а также показать своей жене мучительную смерть её возлюбленного,\nарестовал Ферокса и отправил его сражаться на гладиаторских боях.",
            parent=self,
            scale=1,
            y=-0.3,
            x=-0.7,
            background=True,
            # font='path/to/your_font.ttf' # Используем свой шрифт
            )
        self.bg = Entity(
             model='quad',
             parent=self,
             texture='assets/bg4',
             scale=(camera.aspect_ratio, 1),
             z=1,
             add_to_scene_entities=False
             )

    def create_buttons(self):
        self.a = Button(parent=self,
               text="Play",
               text_color=color.black,
               texture='assets/button5.png',
               color=color.white,
               scale=(0.35, 0.15),
               x=-0.35, y=-0.03,
               font=custom_font,
               )
        self.a.text_entity.font = custom_font
        self.a.on_click = self.restart_game

        self.b = Button(parent=self,
               text="Continue",
               text_color = color.black,
               texture='assets/button5.png',
               color=color.white,
               scale=(0.35, 0.15),
               x='center', y=-0.03)
        self.b.text_entity.font = custom_font
        self.b.on_click = self.hide_menu

        self.c = Button(text="Exit",
               text_color = color.black,
               parent=self,
               texture='assets/button5.png',
               color=color.white,
               scale=(0.35, 0.15),
               x=0.35, y=-0.03)
        self.c.text_entity.font = custom_font
        self.c.on_click = application.quit
        
        self.a.on_mouse_enter = Func(self.a.animate_scale, (0.32, 0.11), duration=0.1)
        self.a.on_mouse_exit = Func(self.a.animate_scale, (0.35, 0.15), duration=0.1)
        self.b.on_mouse_enter = Func(self.b.animate_scale, (0.32, 0.11), duration=0.1)
        self.b.on_mouse_exit = Func(self.b.animate_scale, (0.35, 0.15), duration=0.1)
        self.c.on_mouse_enter = Func(self.c.animate_scale, (0.32, 0.11), duration=0.1)
        self.c.on_mouse_exit = Func(self.c.animate_scale, (0.35, 0.15), duration=0.1)

    def toggle_menu(self):
        if self.enabled:
            self.hide_menu()
        else:
            self.show_menu()

    def show_menu(self):
        global game_is_paused
        game_is_paused = True
        self.enable()
        mouse.locked = False
        mouse.visible = True

    def hide_menu(self):
        global game_is_paused
        self.overlay = Entity(
                    parent=self,
                    model='quad',
                    scale=(camera.aspect_ratio, 1),
                    color=color.black66, # Число 66 — это прозрачность
                    z=2 # Слой за кнопками
                    )
        game_is_paused = False
        self.enabled = False
        if not self.first_run:
            self.title.enabled = False
            self.story.enabled = False
            self.bg.enabled = False
            self.overlay.enabled = True
            self.title_bg.enabled = False
        else:
            self.title.enabled = True
            self.story.enabled = True
            self.bg.enabled = True
        mouse.locked = True
        mouse.visible = False
        
    def restart_game(self):
        self.first_run = False
        if self.on_restart_call:
            self.on_restart_call()
        self.hide_menu()