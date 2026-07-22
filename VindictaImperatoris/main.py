from ursina import *
import classes as cl
from random import randint
from ursina.shaders import basic_lighting_shader, unlit_shader


app = Ursina(development_mode=False)
light_pivot = Entity()
Sky()
player = cl.Player()
cl.game_is_paused = True 
game_over = False
if not game_over:   game_active = False
colosseum = Entity(model='9.glb', collider='box', position=(0, 0, 0), shader=unlit_shader)

directional_light = DirectionalLight(parent=light_pivot, shadows=True)
directional_light.rotation = (45, -45, 0)

window.fullscreen = True
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))

def reset_world():
    cl.game_is_paused = False
    mouse.locked = True
    mouse.visible = False
    if player:
        player.hp_player = 100
        player.phb.value = 100
        player.position = (0, 0.2, 0)
        player.rotation = (0, 0, 0)
    for e in [e for e in scene.entities if isinstance(e, cl.Npc)]:
        destroy(e)
    new_x = random.uniform(-20, 20)
    new_z = random.uniform(15, 30)
    cl.Npc(player_instance=player, speed=15, position=(new_x, 0.5, new_z))
menu = cl.MainMenu(on_restart_call=reset_world)

def input(key): ##отзывчивость кнопок
    if key == 'escape':
        if not menu.enabled:
            menu.show_menu()
        else:
            menu.hide_menu()
    if not cl.game_is_paused and key == 'left mouse down':
        for e in scene.entities:
            if isinstance(e, cl.Npc):
                if player.intersects(e).hit:
                    damage = randint(15, 25)
                    e.account_npc_hp(damage)
                Audio(sound_file_name='hero.mp3', 
                        volume=1, 
                        pitch=1, 
                        balance=0, 
                        loop=False, 
                        loops=1, 
                        autoplay=True, 
                        auto_destroy=False, 
                        group='sfx'
    )

        
def update():
    if cl.game_is_paused:
        return
    if player.hp_player <= 0:
        menu.finish_game() 

if __name__ == "__main__":
    app.run()

