import random
import time
from ursina import *
from random import randint
from direct.actor.Actor import Actor
from ursina.shaders import basic_lighting_shader, unlit_shader
from ursina.prefabs.health_bar import HealthBar

custom_font = 'fonts/antikytheralaser.ttf'
game_is_paused = True 

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(collider='box', speed=35, color=color.white,
                         jump_height=0.5, texture='white_cube', position=(0, 0.2, 0), hp_player=100, shader=basic_lighting_shader, **kwargs)
        self.visual = loader.loadModel("assets/humen_6.glb")
        self.visual.reparentTo(self) 
        self.mouse_sensitivity = 30
        camera.reparent_to(self)
        self.on_ground = False
        self.is_blocking = False


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
        if key == 'right mouse down':
            self.is_blocking = True
        if key == 'right mouse up':
            self.is_blocking = False

    def update(self):
        self.phb.enabled = not game_is_paused
        if game_is_paused:
            return
        self.rotation_y += mouse.velocity.x * self.mouse_sensitivity
        camera.rotation_x -= mouse.velocity.y * self.mouse_sensitivity
        camera.rotation_x = clamp(camera.rotation_x, -89, 89) 
        direction = Vec3(self.forward * (held_keys['w'] - held_keys['s']) +
                     self.right * (held_keys['d'] - held_keys['a'])).normalized()
        self.position += direction * self.speed * time.dt


class Npc(Entity):
    def __init__(self, player_instance, speed=15, **kwargs):
        super().__init__(model='humen_6.glb', collider='box',
                         color=color.gray, texture='white_cube', hp_npc=100, shader=basic_lighting_shader, **kwargs)
        self.player = player_instance 
        self.base_speed = speed
        self.speed = 0
        self.can_move = True
        self.velocity_y = 0
        self.gravity = 0.8
        invoke(self.enable_movement, delay=2)
        self.npc = None
        self.can_attack = True
        
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
    
    def account_npc_hp(self, damage): ##расчет хп нпс
        self.hp_npc -= damage
        self.nhb.value = self.hp_npc        
        if self.hp_npc <= 0:
            new_x = random.uniform(-20, 20)
            new_z = random.uniform(15, 30)
            Npc(player_instance=self.player, speed=self.base_speed, position=(new_x, 0.5, new_z))
            destroy(self)
    
    def reset_attack(self): ##возможность у нпс атаковать
            self.can_attack = True

    def update(self):
        global game_is_paused
        if game_is_paused or not self.player:
            return
        self.look_at(self.player.position)
        self.rotation_x = 0
        self.rotation_z = 0

        distance = distance_xz(self.position, self.player.position)
        if distance > 3:
            self.position += self.forward * self.speed * time.dt
        if self.can_attack and self.intersects(self.player).hit:
            self.attack_logic()

    def attack_logic(self):
        sfx = Audio('npc.mp3', volume=1, autoplay=True) 
        self.can_attack = False
        if self.player.is_blocking:
            Audio(
            'schit.mp3', 
            loop=False,          
            autoplay=True,       
            auto_destroy=False   
            )
            damage = 0
        else:
            damage = randint(7, 15)
            self.player.hp_player -= damage
            self.player.phb.value -= damage
            Audio(sound_file_name='npc.mp3', 
                    volume=1, 
                    pitch=1, 
                    balance=0, 
                    loop=False, 
                    loops=1, 
                    autoplay=True, 
                    auto_destroy=False, 
                    group='sfx')
        invoke(self.reset_attack, delay=2)

class MainMenu(Entity):
    def __init__(self, on_restart_call, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.first_run = True 
        self.on_restart_call = on_restart_call
        self.muse = Audio(
            'menu.mp3', 
            loop=True,          
            autoplay=True,       
            auto_destroy=False   
        )

        self.create_buttons()
        self.create_title()
        self.show_menu()
        

    def create_title(self):
        self.title_bg = Entity(
            parent=self,
            model='quad',
            texture='assets/bg_title.png',
            origin=(0,0),
            scale=(1, 0.15),
            position=(0, 0.25),
            color=color.white,
            )

        self.title = Text(text="VINDICTA IMPERATORIS",
            parent=self,
            scale=3,
            color=color.black,
            origin=(0,0),
            position=(0, 0.24),
            font=custom_font,
            )

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
        self.overlay = Entity(
                    parent=self,
                    model='quad',
                    scale=(camera.aspect_ratio, 1),
                    color=color.black66,
                    z=2,
                    enabled = False,
                    )

    def create_buttons(self):
        self.a = Button(parent=self,
               text="Play",
               text_color=color.black,
               texture='assets/button5.png',
               color=color.white,
               scale=(0.35, 0.15),
               x = -0.2, y=-0.03,
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
               y=-0.03)
        self.b.text_entity.font = custom_font
        self.b.on_click = self.hide_menu

        self.c = Button(text="Exit",
               text_color = color.black,
               parent=self,
               texture='assets/button5.png',
               color=color.white,
               scale=(0.35, 0.15),
               x=0.20, y=-0.03)
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
            Audio(sound_file_name='menu.mp3', 
                        volume=1, 
                        pitch=1, 
                        balance=0, 
                        loop=False, 
                        loops=1, 
                        autoplay=True, 
                        auto_destroy=False, 
                        group='sfx')

    def restart_game(self):
        self.muse.stop()
        if self.on_restart_call:
            self.on_restart_call()
        self.first_run = False
        self.enabled = False
        self.bg.enabled = False
        self.story.enabled = False
        self.title.text = "VINDICTA IMPERATORIS"
        self.title.color = color.black
        self.title.scale = 3
        game_is_paused = False
        mouse.locked = True
        mouse.visible = False

    def show_menu(self):
        global game_is_paused
        if not self.muse.playing:
            self.muse.play()
        game_is_paused = True
        self.enabled = True
        self.bg.enabled = True
        if not self.first_run:                  ## ПАУЗА
            self.b.x = -0.2
            self.overlay.enabled = True
            self.bg.enabled = False
            self.title.text = "PAUSE"
            self.title.scale = 3
            self.story.enabled = False
            self.a.enabled = False
            self.b.enabled = True
        else:                                   ## ЗАПУСК
            self.overlay.enabled = False
            self.bg.enabled = True
            self.story.enabled = True
            self.a.enabled = True
            self.b.enabled = False
        mouse.locked = False
        mouse.visible = True

    def hide_menu(self):
        global game_is_paused
        self.muse.fade_out(duration=0.5)
        game_is_paused = False
        self.enabled = False
        self.bg.enabled = False
        self.overlay.enabled = False
        self.first_run = False

    def finish_game(self):
        global game_is_paused
        self.a.x = -0.2
        self.a.enabled = True
        game_is_paused = True
        self.enabled = True
        self.overlay.enabled = True
        self.bg.enabled = False
        self.title.text = "GAME OVER"
        self.title.enabled = True
        self.story.enabled = False
        self.b.enabled = False
        mouse.locked = False

