import pygame, numpy
import math

WIDTH = 1920
HEIGHT = 1080
BACKGROUND = (55, 110, 100)

SQUARE_ROOT_OF_TWO = math.sqrt(2)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, image, startx, starty, group):
        super().__init__(group)

        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(startx, starty))

    def update(self):
        pass

    def event(self, **kwargs):
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Wall_H(Sprite):
    def __init__(self, startx, starty, group):
        super().__init__("TempWall_H.png", startx, starty, group)


class Wall_V(Sprite):
    def __init__(self, startx, starty, group):
        super().__init__("TempWall_V.png", startx, starty, group)


class Wall_H_JD(Sprite):
    def __init__(self, startx, starty, group):
        super().__init__("TempWall_H_JD.png", startx, starty, group)


class Wall_VE_JU(Sprite):
    def __init__(self, startx, starty, group):
        super().__init__("TempWall_VE_JU.png", startx, starty, group)


class Barrier(Sprite):
    def __init__(self, startx, starty, group):
        super().__init__("Barrier.png", startx, starty, group)


class SadBarrier(Barrier):
    def event(self, player):
        player.stand_image = pygame.image.load("p1_front_cry.png").convert_alpha()


class HappyBarrier(Barrier):
    def event(self, player):
        player.stand_image = pygame.image.load("p1_front.png").convert_alpha()


class Player(pygame.sprite.Sprite):
    def __init__(self, startx, starty, group, boxes):
        super().__init__(group)
        self.image = pygame.image.load("p1_front.png").convert_alpha()
        self.rect = self.image.get_rect(center=(startx, starty))

        self.stand_image = self.image
        self.jump_image = pygame.image.load("p1_jump.png").convert_alpha()

        self.walk_cycle = [
            pygame.image.load(f"p1_walk{i:0>2}.png") for i in range(1, 12)
        ]

        self.boxes = boxes

        self.animation_index = 0
        self.facing_left = False

        self.speed = 8
        self.jumpspeed = 20
        self.vsp = 0
        self.gravity = 0
        self.min_jumpspeed = 4
        self.prev_key = pygame.key.get_pressed()

    def walk_animation(self):
        self.image = self.walk_cycle[self.animation_index]
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.animation_index < len(self.walk_cycle) - 1:
            self.animation_index += 1
        else:
            self.animation_index = 0

    def jump_animation(self):
        self.image = self.jump_image
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """
        TODO Document this method.
        """
        hsp = 0
        vsp = 0
        onground = self.check_collision(0, 1, grounds=self.boxes)
        # check keys
        keys = pygame.key.get_pressed()

        hsp = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        vsp = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed

        # MOVEMENT ANIMATION DISABLED FOR SIMPLIFIED TESTING [1]

        # if hsp < 0:
        #    self.facing_left = True
        #    self.walk_animation()

        # else:
        #    self.facing_left = False
        #    self.walk_animation()

        # END OF DISABLE [1]

        if hsp * vsp != 0:
            hsp /= SQUARE_ROOT_OF_TWO
            vsp /= SQUARE_ROOT_OF_TWO
        if hsp == vsp == 0:
            self.image = self.stand_image

        # TODO This is a relic, should be removed if we do not use jumping.
        if self.prev_key[pygame.K_UP] and not keys[pygame.K_UP]:
            if self.vsp < -self.min_jumpspeed:
                self.vsp = -self.min_jumpspeed

        self.prev_key = keys

        # movement
        self.move(hsp, vsp)

    def move(self, x, y):
        dx = x
        dy = y

        while self.check_collision(0, dy, self.boxes):
            dy -= numpy.sign(dy)

        while self.check_collision(dx, dy, self.boxes):
            dx -= numpy.sign(dx)

        self.rect.move_ip([dx, dy])

    def check_collision(self, x, y, grounds):
        self.rect.move_ip([x, y])
        collide = pygame.sprite.spritecollideany(self, grounds)
        if collide:
            collide.event(player=self)

        self.rect.move_ip([-x, -y])
        return collide


class CameraGroup(pygame.sprite.Group):
    """
    The CameraGroup class is a subclass of pygame.sprite.Group that
    automatically adjusts the position of all sprites in the group
    based on the position of the player. In other words, it works in
    such a way that when the player "moves", the player doesn't really
    move. Instead everything else moves around the player to give the
    illusion of the player navigating the environment, while also keeping
    the player at the center of the screen.
    """

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # Camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] / 2
        self.half_h = self.display_surface.get_size()[1] / 2

        # Box setup
        # These are the parameters that define the box that the player can move
        # around in when using the box_center_camera method.
        self.camera_borders = {"left": 600, "right": 600, "top": 350, "bottom": 350}
        left = self.camera_borders["left"]
        top = self.camera_borders["top"]
        width = self.display_surface.get_size()[0] - (
            self.camera_borders["left"] + self.camera_borders["right"]
        )
        height = self.display_surface.get_size()[1] - (
            self.camera_borders["top"] + self.camera_borders["bottom"]
        )
        self.camera_rect = pygame.Rect(left, top, width, height)

        # Keyboard camera speed
        self.keyboard_camera_speed = 8


    def center_target_camera(self, target):
        """
        Readjusts the offset parameter base on the target's location.
        This camera option will keep the target at the center of the
        screen.
        """
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def box_target_camera(self, target):
        """
        Readjusts the offset parameter base on the target's location.
        This camera option will keep the target within a "camera box"
        that is centered on the screen.
        """
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]

    def keyboard_control_camera(self, target):
        """
        Readjusts the offset parameter based on the keyboard input.
        This camera option will allow the user to move the camera
        around the screen using WASD.
        """
        if target.prev_key[pygame.K_a]:
            self.camera_rect.x -= self.keyboard_camera_speed
        if target.prev_key[pygame.K_d]:
            self.camera_rect.x += self.keyboard_camera_speed
        if target.prev_key[pygame.K_w]:
            self.camera_rect.y -= self.keyboard_camera_speed
        if target.prev_key[pygame.K_s]:
            self.camera_rect.y += self.keyboard_camera_speed
        
        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]



    def custom_draw(self, player):
        """
        Draws all sprites in the group, but first adjusts the position
        of each sprite based on the offset parameter.
        """
        # Use the camera where the player is exactly in the middle of the screen
        self.center_target_camera(player)

        # Use the box camera where the player is in the middle of the screen
        self.box_target_camera(player)

        # Use the keyboard camera where the player can move the camera with WASD
        self.keyboard_control_camera(player)

        # active elements
        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    camera_group = CameraGroup()
    boxes = pygame.sprite.Group()

    for bx in range(0, 2000, 70):
        boxes.add(Wall_H(bx, 100, camera_group))  # Wall horizontal top row
        boxes.add(Wall_H(bx, 1035, camera_group))  # Wall horizontal bottom row

    for bx in range(5):
        for by in range(170, 660, 70):
            boxes.add(Wall_V(bx * 490, by, camera_group))  # Wall vertical
            boxes.add(
                Wall_VE_JU(bx * 490, 730, camera_group)
            )  # Wall vertical end blocks
            boxes.add(
                Wall_H_JD(bx * 490, 100, camera_group)
            )  # Wall horizontal top junctions
        for i in range(3):
            boxes.add(
                Wall_H(((i - 1) * 70) + (bx * 490), 660, camera_group)
            )  # Wall horizontal middle chunks
        for i in range(3):
            boxes.add(
                Barrier((i * 70) + 630, 660, camera_group)
            )  # Barrier blocking access to one room

        boxes.add(SadBarrier((3 * 70) + 630, 800, camera_group))
        boxes.add(HappyBarrier((6 * 70) + 630, 800, camera_group))

    player = Player(
        100, 900, camera_group, boxes
    )  # Player start location [WIDTH / 2, HEIGHT / 2]

    while True:
        pygame.event.pump()
        # player.update(boxes)

        # Draw loop
        screen.fill(BACKGROUND)
        # player.draw(screen)
        # boxes.draw(screen)
        # pygame.display.flip()

        camera_group.update()
        camera_group.custom_draw(player)

        pygame.display.update()

        clock.tick(60)


if __name__ == "__main__":
    main()
