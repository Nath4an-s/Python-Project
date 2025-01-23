import pygame
from pygame.constants import HWSURFACE 
from .utils import *


class Hud:

    def __init__(self, resource_manager, width, height):

        self.resource_manager = resource_manager
        self.width = width
        self.height = height

        self.hud_colour = (198, 155, 93, 175)

        self.images = self.load_images()
        self.images_hud = self.load_images_hud()
        self.images_scale = self.load_images_scale()
        self.images_icons = self.load_unit_icons()
        self.towncenter_icons = self.load_towncenter_icons()

        #Screen sized hud 
        self.hudmoi_surface = pygame.Surface((width,height),pygame.SRCALPHA) 

        # resouces hud (Text box top left. Should be changed) 
        self.resources_surface = pygame.Surface((width*0.42, height * 0.07), pygame.SRCALPHA)
        self.resources_rect = self.resources_surface.get_rect(topleft=(0, 0))

        # age hud
        self.age_surface = pygame.Surface((width*0.153, height * 0.06), pygame.SRCALPHA)
        self.age_rect = self.age_surface.get_rect(topleft=(0, 0))

        # building hud (Bottom left) 
        self.build_surface = pygame.Surface((width * 0.32, height * 0.21), pygame.SRCALPHA)
        self.build_rect = self.build_surface.get_rect(topleft=(0, self.height * 0.79))

        # select hud (Bottom right) 
        self.select_surface = pygame.Surface((width * 0.41, height * 0.193), pygame.SRCALPHA)
        self.select_rect = self.select_surface.get_rect(topleft=(self.width * 0.35, self.height * 0.79))
        self.select_surface_empty = True

        #Display unit and building icons boolean
        self.display_unit_icons = False
        self.display_building_icons = False
        self.display_towncenter_icons = False

        #fonts for units hp
        self.font = pygame.font.SysFont("arialblack", 10)

        self.unit_icons = []
        self.tiles = self.create_build_hud()
        self.create_ressource_hud()

        self.selected_unit_icon = None
        self.selected_towncenter_icon = None
        self.selected_tile = None
        self.examined_tile = None

        

    def create_build_hud(self):

        self.build_surface.blit(self.images_hud["hudbuild"],(0,0))

        self.age_surface.blit(self.images_hud["hudAge"],(0,0))
        
        render_pos = [20, self.height-self.height * 0.21 + 35]
        unit_icons_render_pos = [19, self.height-self.height * 0.21 + 35]
        towncenter_icons_render_pos = [19, self.height-self.height * 0.21 + 35]
        object_width = self.build_surface.get_width() // 10

        tiles = []
        unit_icons = []
        towncenter_icons = []

        for image_name, image in self.images.items():

            pos = render_pos.copy()
            pos = [pos[0] -5 , pos[1]]
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=object_width + 20)
            rect = image_scale.get_rect(topleft=pos)            

            tiles.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images[image_name],
                    "rect": rect,
                    "affordable": True
                }
            )

            render_pos[0] += int(self.build_surface.get_width() // 10)
        
        for image_name, image in self.images_icons.items():

            pos = unit_icons_render_pos.copy()
            pos = [pos[0] + 10, pos[1]]
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=object_width)
            rect = image_scale.get_rect(topleft=pos)            

            unit_icons.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.images_icons[image_name],
                    "rect": rect,
                    "affordable": True
                }
            )

            unit_icons_render_pos[0] += self.build_surface.get_width() // 10
        self.unit_icons = unit_icons    
        
        for image_name, image in self.towncenter_icons.items():

            pos = towncenter_icons_render_pos.copy()
            pos = [pos[0] + 12, pos[1] - 4]
            image_tmp = image.copy()
            image_scale = self.scale_image(image_tmp, w=object_width)
            rect = image_scale.get_rect(topleft=pos)            

            towncenter_icons.append(
                {
                    "name": image_name,
                    "icon": image_scale,
                    "image": self.towncenter_icons[image_name],
                    "rect": rect,
                    "affordable": True
                }
            )

            towncenter_icons_render_pos[0] += int(self.build_surface.get_width() // 1.73)
        self.towncenter_icons = towncenter_icons   

        return tiles
    
    def create_ressource_hud(self):
        self.resources_surface.blit(self.images_hud["hudRessources"],(0,0))

    def update(self):

        mouse_pos = pygame.mouse.get_pos()
        mouse_action = pygame.mouse.get_pressed()

        if mouse_action[2]:
            self.selected_tile = None

        if self.display_building_icons:
            for tile in self.tiles:
                if self.resource_manager.is_affordable(tile["name"]):
                   tile["affordable"] = True
                else:
                   tile["affordable"] = False
                if tile["rect"].collidepoint(mouse_pos) and tile["affordable"]:
                   if mouse_action[0]:
                       self.selected_tile = tile
        
        elif self.display_unit_icons:
            for icon in self.unit_icons:
                if self.resource_manager.is_affordable(icon["name"]) and self.resource_manager.population < self.resource_manager.max_population:
                   icon["affordable"] = True
                else:
                   icon["affordable"] = False
                if icon["rect"].collidepoint(mouse_pos) and icon["affordable"]:
                   if mouse_action[0]:
                       self.selected_unit_icon = icon
        
        elif self.display_towncenter_icons:
            for icon in self.towncenter_icons:
                if self.resource_manager.is_affordable(icon["name"]) and self.resource_manager.population < self.resource_manager.max_population:
                   icon["affordable"] = True
                else:
                   icon["affordable"] = False
                if icon["rect"].collidepoint(mouse_pos) and icon["affordable"]:
                   if mouse_action[0]:
                       self.selected_towncenter_icon = icon

                        


    def draw(self, screen):

        #if not self.hudmoi_surface_empty: screen.blit(self.hudmoi_surface,(0,0))
        screen.blit(self.resources_surface,(0,0))
        #screen.blit(self.age_surface,(300,300))
        
        # build pannel hud (Bottom left) 
        screen.blit(self.build_surface, (0, self.height-self.height * 0.21)) 

        #select hud (Bottom right) 
        if not self.select_surface_empty: 
            screen.blit(self.select_surface, (self.width*0.599 , self.height*0.81))
            screen.blit(self.unit_pv_img, (round(self.width * 0.64), round(self.height * 0.96))) 
            screen.blit(self.unit_ressource_img, (round(self.width * 0.67), round(self.height * 0.94))) 

        #Top right hud
        screen.blit(self.age_surface, (self.width * 0.85, 0))

        # resources (Text box top right. Should be changed) 
        screen.blit(self.resources_surface, (0,0))
        pos = 75
        for resource, resource_value in self.resource_manager.resources.items():
            txt = str(resource_value)
            draw_text(screen, txt, 20, (255, 255, 255), (pos, 22))
            pos += 108
        
        if self.display_building_icons:
            for tile in self.tiles:
                screen.blit(tile["icon"], tile["rect"].topleft)
        elif self.display_unit_icons:
            for icon in self.unit_icons:
                 screen.blit(icon["icon"], icon["rect"].topleft)   
        elif self.display_towncenter_icons:
            for icon in self.towncenter_icons:
                 screen.blit(icon["icon"], icon["rect"].topleft)   

    
    def blit_hud(self, imgtoblit, pv, screen, ressource="", type_ressource="", population="", max_population=""):
        self.select_surface_empty = False
        self.select_surface.blit(self.images_hud[imgtoblit], (0, 0))
        self.unit_pv_img = self.font.render(pv, True, WHITE)
        self.unit_ressource_img = self.font.render(type_ressource + " " + ressource + " Population   " + population + "        Population maximum   " + max_population, True, WHITE)        

    def load_images(self):

        # read images
        house = pygame.image.load("assets/house.png").convert_alpha()
        hudVillagois = pygame.image.load("assets/HUD/Hud_Villageois_1920-1080.png").convert_alpha()
        barrack = pygame.image.load("assets/barrack.png").convert_alpha()
        storage = pygame.image.load("assets/Stable128-64.png").convert_alpha()
        farm = pygame.image.load("assets/stable_tool.png").convert_alpha()
        hudRessources = pygame.image.load("assets/HUD/Hud1v1.png").convert_alpha()
        hudAge = pygame.image.load("assets/HUD/Hud1v1_Age.png").convert_alpha()

        images = {
            "House": house,
            "Barrack": barrack,
            "Storage" : storage,
            "Farm" : farm
        }
        return images

    def load_images_scale(self):

        # read images
        house = pygame.image.load("assets/house.png").convert_alpha()
        hudVillageois = pygame.image.load("assets/HUD/Hud_Villageois_1920-1080.png").convert_alpha()
        barrack = pygame.image.load("assets/barrack.png").convert_alpha()
        storage = pygame.image.load("assets/Stable128-64.png").convert_alpha()
        farm = pygame.image.load("assets/stable_tool.png").convert_alpha()
        hudRessources = pygame.image.load("assets/HUD/Hud1v1.png").convert_alpha()
        hudAge = pygame.image.load("assets/HUD/Hud1v1_Age.png").convert_alpha()

        images = {
            "House": house,
            "Barrack": barrack,
            "Storage" : storage,
            "Farm" : farm
        }
        return images

    def load_unit_icons(self):
        iconSoldier = pygame.image.load("assets/HUD/icone_fantassinMassue.png").convert_alpha()
        iconHorseman = pygame.image.load("assets/HUD/icone_cavalier.png").convert_alpha()
        iconArcher = pygame.image.load("assets/HUD/icone_archer.png").convert_alpha()

        images = {
            "Soldier" : iconSoldier,
            "Archer" : iconArcher,
            "horseman" : iconHorseman
        }
        return images      

    def load_towncenter_icons(self):
        iconVillageois = pygame.image.load("assets/HUD/icone_villageois.png").convert_alpha()
        iconPassage_Age = pygame.image.load("assets/HUD/icone_passageAge2.png").convert_alpha()

        images = {
            "Villageois" : iconVillageois,
            "Passage_Age" : iconPassage_Age,
        }
        return images       

    def load_images_hud(self):

        # read images
        hudVillageois = pygame.image.load("assets/HUD/Hud_Villageois_1920-1080.png").convert_alpha()
        hudRessources = pygame.image.load("assets/HUD/Hud1v1.png").convert_alpha()
        hudAge = pygame.image.load("assets/HUD/Hud1v1_Age.png").convert_alpha()
        hudAge2 = pygame.image.load("assets/HUD/Hud1v1_Age2.png").convert_alpha()
        hudArbre= pygame.image.load("assets/HUD/Hud_Arbre_1920-1080.png").convert_alpha()
        hudBuisson = pygame.image.load("assets/HUD/Hud_Forum_1920-1080.png").convert_alpha()
        hudMineOr = pygame.image.load("assets/HUD/Hud_MineOr_1920-1080.png").convert_alpha()
        hudMinePierre = pygame.image.load("assets/HUD/Hud_MinePierre_1920-1080.png").convert_alpha()
        hudPuitStockage = pygame.image.load("assets/HUD/Hud_Puit_stockage_1920-1080.png").convert_alpha()
        hudGrenier = pygame.image.load("assets/HUD/Hud_Grenier_1920-1080.png").convert_alpha()
        hudHouse = pygame.image.load("assets/HUD/Hud_hutte_1920-1080.png").convert_alpha()
        hudTowncenter = pygame.image.load("assets/HUD/Hud_Forum_1920-1080.png").convert_alpha()
        hudEcurie = pygame.image.load("assets/HUD/Hud_Ecurie_1920-1080.png").convert_alpha()
        hudCaserne = pygame.image.load("assets/HUD/Hud_Caserne_1920-1080.png").convert_alpha()
        hudCampArchers = pygame.image.load("assets/HUD/Hud_CampTireArc_1920-1080.png").convert_alpha()
        hudSoldier = pygame.image.load("assets/HUD/Hud_FantassinMassue_1920-1080.png").convert_alpha()
        hudCavalier = pygame.image.load("assets/HUD/Hud_Cavalier_1920-1080.png").convert_alpha()
        hudArcher = pygame.image.load("assets/HUD/Hud_Archer_1920-1080.png").convert_alpha()
        hudbuild = pygame.image.load("assets/HUD/build_hud.png").convert_alpha()
        hudBigdaddy = pygame.image.load("assets/HUD/Hud_FantassinMassue_1920-1080.png").convert_alpha()
        hudFarm = pygame.image.load("assets/HUD/Hud_Farm_1920-1080.png").convert_alpha()
        
        images = {
            "hudVillageois": hudVillageois,
            "hudRessources": hudRessources,
            "hudAge": hudAge,
            "hudAge2": hudAge2,
            "hudTowncenter": hudTowncenter,
            "hudArbre":hudArbre,
            "hudBuisson":hudBuisson ,
            "hudMineOr":hudMineOr ,
            "hudMinePierre":hudMinePierre ,
            "hudPuitStockage":hudPuitStockage ,
            "hudGrenier":hudGrenier ,
            "hudHouse":hudHouse ,
            "hudEcurie":hudEcurie ,
            "hudCaserne":hudCaserne ,
            "hudCampArchers":hudCampArchers ,
            "hudSoldier":hudSoldier,
            "hudCavalier":hudCavalier,
            "hudArcher":hudArcher,
            "hudbuild":hudbuild,
            "hudBigdaddy":hudBigdaddy,
            "hudFarm":hudFarm
        }
        return images

    def scale_image(self, image, w=None, h=None):

        if (w == None) and (h == None):
            pass
        elif h == None:
            scale = w / image.get_width()
            h = scale * image.get_height()
            image = pygame.transform.scale(image, (int(w), int(h))).convert_alpha()
        elif w == None:
            scale = h / image.get_height()
            w = scale * image.get_width()
            image = pygame.transform.scale(image, (int(w), int(h))).convert_alpha()
        else:
            image = pygame.transform.scale(image, (int(w), int(h))).convert_alpha()

        return image
