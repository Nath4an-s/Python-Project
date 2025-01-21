import pygame
import sys

class OffsetTester:
    def __init__(self, image_paths, window_size=(800, 600), target_position=None):
        # Initialisation de Pygame
        pygame.init()
        
        # Configuration de la fenêtre
        self.window_width, self.window_height = window_size
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Test Offset")
        
        # Charger les images
        self.image_paths = image_paths
        self.current_image_index = 0
        self.load_image(self.current_image_index)
        
        # Position cible (où le point rouge doit être affiché)
        if target_position is None:
            self.target_position = (self.window_width // 2, self.window_height // 2)
        else:
            self.target_position = target_position
        
        # Variables pour le déplacement
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
    
    def load_image(self, index):
        """Charge l'image à l'index donné."""
        try:
            self.image = pygame.image.load(self.image_paths[index])
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image : {e}")
            sys.exit()
        self.image_rect = self.image.get_rect()
        self.image_rect.center = (self.window_width // 2, self.window_height // 2)
    
    def run(self):
        # Boucle principale
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Navigation avec les flèches
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:  # Image suivante
                        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
                        self.load_image(self.current_image_index)
                    elif event.key == pygame.K_LEFT:  # Image précédente
                        self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
                        self.load_image(self.current_image_index)
                
                # Détecter le clic pour commencer à déplacer
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.image_rect.collidepoint(event.pos):  # Si clic sur l'image
                        self.dragging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.image_rect.x - mouse_x
                        self.offset_y = self.image_rect.y - mouse_y
                
                # Arrêter le déplacement
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                
                # Déplacer l'image
                if event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mouse_x, mouse_y = event.pos
                        self.image_rect.x = mouse_x + self.offset_x
                        self.image_rect.y = mouse_y + self.offset_y
            
            # Affichage de l'image
            self.screen.fill((255, 255, 255))  # Fond blanc
            self.screen.blit(self.image, self.image_rect)
            
            # Affichage du point rouge (position cible)
            pygame.draw.circle(self.screen, (255, 0, 0), self.target_position, 5)
            
            # Calcul des offsets relatifs
            relative_offset_x = self.image_rect.x - self.target_position[0]
            relative_offset_y = self.image_rect.y - self.target_position[1]
            
            # Affichage des offsets relatifs
            font = pygame.font.Font(None, 36)
            offset_text = font.render(
                f"Offset: ({relative_offset_x}, {relative_offset_y})", True, (0, 0, 0)
            )
            self.screen.blit(offset_text, (10, 10))
            
            # Affichage du nom de l'image actuelle
            image_name = self.image_paths[self.current_image_index].split("\\")[-1]
            image_text = font.render(f"Image: {image_name}", True, (0, 0, 0))
            self.screen.blit(image_text, (10, 50))
            
            # Mise à jour de l'écran
            pygame.display.flip()

# Exemple d'utilisation
if __name__ == "__main__":
    # Chemins des images à tester
    image_paths = [
        r"C:\Users\natsa\Documents\Programmation\Python-Project\assets\units\villager\FarmingVillager\Farm\Attack\Villageract001.png",   # Exemple pour l'état "gathering"
        r"C:\Users\natsa\Documents\Programmation\Python-Project\assets\units\villager\FarmingVillager\Build & Repair\Act\Villageract001.png", # Exemple pour l'état "constructing"
        r"C:\Users\natsa\Documents\Programmation\Python-Project\assets\units\villager\attack\Villagerattack001.png"   # Exemple pour l'état "attacking"
    ]
    
    # Position cible (où le point rouge doit apparaître)
    target_position = (400, 300)  # Position au centre de la fenêtre
    
    # Lancer le test
    tester = OffsetTester(image_paths, target_position=target_position)
    tester.run()
