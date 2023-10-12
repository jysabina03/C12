# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDLK_a


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def a_down(e):
    return e[0]=='INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def time_out(e):
    return e[0] == 'TIME_OUT'


class Idle:

    @staticmethod
    def enter(boy,e):
        if boy.action==0:
            boy.action=2
        elif boy.action==1:
            boy.action=3

        boy.frame = 0
        boy.start_time = get_time()
        print('Idle Enter')

    @staticmethod
    def exit(boy,e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class Sleep:

    @staticmethod
    def enter(boy,e):
        boy.frame = 0
        print('sleep Enter / 고개 숙이기')

    @staticmethod
    def exit(boy,e):
        print('sleep Exit / 고개 들기')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('sleep Do / 드르렁')

    @staticmethod
    def draw(boy):
        if boy.action==2:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100, math.pi / -2, '', boy.x + 25,
                                      boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, boy.action * 100, 100, 100, math.pi / 2, '', boy.x - 25,
                                          boy.y - 25, 100, 100)
        pass

class Run:

    @staticmethod
    def enter(boy,e):
        if right_down(e) or left_up(e):
            boy.dir,boy.action=1,1
        elif left_down(e) or right_up(e):
            boy.dir,boy.action=-1,0

        print('Run Enter / 달리기 시작')

    @staticmethod
    def exit(boy,e):
        print('Run Exit / 달리기 멈춤')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        print('Run Do / 달리는 중')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass


class AutoRun:

    @staticmethod
    def enter(boy,e):

        if boy.action == 2:
            boy.dir=-1
        elif boy.action == 3:
            boy.dir=1

        boy.frame = 0
        boy.start_time = get_time()
        print('AutoRun Enter')

    @staticmethod
    def exit(boy,e):
        print('AutoRun Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 10
        if get_time() - boy.start_time > 5.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))
        print('AutoRun Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_composite_draw(boy.frame * 100, (boy.action-2) * 100, 100, 100, 0,'',boy.x, boy.y,200,200)
        pass


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.table = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep,a_down:AutoRun},
            Run: {right_down: Idle, left_down: Idle, left_up: Idle, right_up: Idle},
            Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle},
            AutoRun: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Idle},
                      }

    def start(self):
        self.cur_state.enter(self.boy,('START',0))

    def update(self):
        self.cur_state.do(self.boy)

    def handle_event(self, e):  # STATE EVENT handling
        for cheak_event, next_state in self.table[self.cur_state].items():
            if cheak_event(e):
                self.cur_state.exit(self.boy,e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy,e)
                return True  # t성공적ㅇ으로 이벤트 변환
        return False  # 이벤트ㅡㄹㄹ 소모하지 못했다

    def draw(self):
        self.cur_state.draw(self.boy)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # pico2d 이벤트를 -> state machine 으로 바꿈
        self.state_machine.handle_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()
