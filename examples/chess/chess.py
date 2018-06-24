import sys
import logging

from rx.subjects import Subject
from rx.concurrency import PyGameScheduler

import pygame

#FORMAT = '%(asctime)-15s %(threadName)s %(message)s'
#logging.basicConfig(format=FORMAT, level=logging.DEBUG)
#log = logging.getLogger('Rx')

def main():
    pygame.init()

    size = width, height = 500, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Rx for Python rocks")

    black = 0, 0, 0
    background = pygame.Surface(screen.get_size())
    background.fill(black)             # fill the background black
    background = background.convert()  # prepare for faster blitting

    scheduler = PyGameScheduler()

    mousemove = Subject()

    files = [
        "chess_tower.png",
        "chess_bishop.png",
        "chess_horse.png",
        "chess_king.png",
        "chess_queen.png",
        "chess_horse.png",
        "chess_bishop.png",
        "chess_tower.png"
        ]
    images = [pygame.image.load(image).convert_alpha() for image in files]

    old = [None] * len(images)
    draw = []
    erase = []

    def handle_image(i, image):
        imagerect = image.get_rect()

        def on_next(ev):
            imagerect.top = ev[1]
            imagerect.left = ev[0] + i * 30

            if old[i]:
                erase.append(old[i])
            old[i] = imagerect.copy()
            draw.append((image, imagerect.copy()))

        def on_error(err):
            print("Got error: %s" % err)
            sys.exit()

        mousemove.delay(i * i * 50, scheduler=scheduler).subscribe(on_next, on_error=on_error)

    for i, image in enumerate(images):
        handle_image(i, image)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                pos = event.pos
                mousemove.on_next(pos)
            elif event.type == pygame.QUIT:
                sys.exit()

        if len(draw):
            update = []
            for rect in erase:
                screen.blit(background, (rect.x, rect.y), rect)
                update.append(rect)

            for image, rect in draw:
                screen.blit(image, rect)
                update.append(rect)

            pygame.display.update(update)
            #pygame.display.flip()
            draw = []
            erase = []

        scheduler.run()

if __name__ == '__main__':
    main()
