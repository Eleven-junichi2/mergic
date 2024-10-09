import pygame

FPS = 60

key_to_filepath = {}

def main():
    pygame.init()
    clock = pygame.time.Clock()
    display = pygame.display.set_mode((640, 360))
    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.fill((0, 0, 0))
        pygame.display.flip()
        dt = clock.tick(FPS) # milliseconds
        print(dt)
    pygame.quit()


if __name__ == '__main__':
    main()
