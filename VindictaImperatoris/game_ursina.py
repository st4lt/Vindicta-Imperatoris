from ursina import *
from ursina.shaders import lit_with_shadows_shader
import classes as cl
from random import randint
from ursina.prefabs.health_bar import HealthBar
from direct.actor.Actor import Actor


app = Ursina() ##создание окна
light_pivot = Entity()
Sky()

game_over = False
if not game_over:   game_active = False
colosseum = Entity(model='kolizey_5.glb', collider='box', position=(0, 0, 0))

directional_light = DirectionalLight(parent=light_pivot, shadows=True)
directional_light.rotation = (45, -45, 0)

window.fullscreen = True
sun = DirectionalLight()
sun.look_at(Vec3(1, -1, 1))


def spawn_npc(): ##появление нпс
    global npc
    if not npc:
        random_x = random.uniform(-30, 30)
        random_z = random.uniform(15, 30)
        npc = cl.Npc(target=player, position=(random_x, 0.2, random_z))


def reset_world(): ##создание мира
    global npc, game_over, game_active
    game_over = False
    game_active = True
    if player:
        player.hp_player = 100
        player.phb.value = 100
        player.position = (0, 0.2, 0)
    if npc:
        destroy(npc)
        npc = None  # Важно обнулить переменную перед spawn_npc
    spawn_npc()

player = cl.Player()
random_x = random.uniform(-30, 30)
random_z = random.uniform(15, 30)
npc = cl.Npc(target=player, position=(random_x, 0.2, random_z))
menu = cl.MainMenu(on_restart_call=reset_world)

def account_npc_hp(damage): ##расчет хп нпс
    global npc
    if not npc: return
    npc.hp_npc -= damage
    npc.nhb.value -= damage
    if npc.hp_npc <= 0:
        npc.shadows = False
        npc.visible = False
        destroy(npc, delay=0.01)
        npc = None
        spawn_npc()
        return

npc.can_attack = True
def reset_attack(): ##возможность у нпс атаковать
    global npc
    if npc and hasattr(npc, 'can_attack'): # Безопасная проверка
        npc.can_attack = True

def finish_game(): ##конец игры
    global game_active, game_over
    game_active = False
    game_over = True
    menu.show_menu()
    mouse.locked = False

def update(): ##логика урона
    global player, npc, game_over, game_active
    # shader_entities = [colosseum, player, npc]
    # for e in shader_entities:
        # if e and hasattr(e, 'shader') and e.shader == custom_shader:
            # e.set_shader_input('light_pos', sun.world_position) # Берем позицию солнца
            # e.set_shader_input('camera_pos', camera.world_position) # Позиция игрока/камеры
            # e.set_shader_input('light_color', Vec3(1, 1, 1))

    if menu.enabled:
        game_active = False
        return
    else:
        game_active = True

    if player and npc: 
        if npc.intersects(player).hit and npc.can_attack:
            npc.can_attack = False
            if hasattr(player, 'is_blocking') and player.is_blocking:
                damage = 0
            else:
                damage = randint(7, 15)
                player.hp_player -= damage
                player.phb.value -= damage
            invoke(reset_attack, delay=2)
            if player.hp_player <= 0:
                game_over = True
                finish_game()

def input(key): ##отзывчивость кнопок
    if key == 'escape':
        menu.toggle_menu()

    if game_active and key == 'left mouse down':
        if npc and player:
            if player.intersects(npc).hit:
                damage = randint(5, 15)
                account_npc_hp(damage)

    if game_active and key == 'right mouse down':
        player.is_blocking = True

    if game_active and key == 'right mouse up':
        player.is_blocking = False
        


if __name__ == "__main__":
    app.run()

