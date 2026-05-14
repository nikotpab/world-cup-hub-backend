import sys
import os
# Add the project root to sys.path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app import create_app
from app.infrastructure.database import db
from app.domain.models.sticker import Sticker
from app.domain.models.rarity_cat import RarityCat
from app.infrastructure.external.football_data_service import FootballDataService

def sync_stickers():
    app = create_app()
    with app.app_context():
        print("Starting sticker synchronization...")
        
        # Ensure rarity categories exist
        rarities = ["Common", "Rare", "Epic", "Legendary"]
        rarity_map = {}
        for r_name in rarities:
            rc = RarityCat.query.filter_by(name=r_name).first()
            if not rc:
                rc = RarityCat(name=r_name)
                db.session.add(rc)
                db.session.commit()
            rarity_map[r_name] = rc.rarityCatId

        # Panini 2026 Data based on checklist
        panini_teams = {
            "USA": ["Antonee Robinson", "Weston McKennie", "Christian Pulisic", "Matt Turner", "Chris Richards", "Tim Ream", "Sergino Dest", "Yunus Musah", "Tyler Adams", "Gio Reyna", "Timothy Weah", "Folarin Balogun", "Ricardo Pepi"],
            "MEX": ["Luis Malagón", "Johan Vasquez", "Jorge Sánchez", "Cesar Montes", "Jesus Gallardo", "Israel Reyes", "Edson Álvarez", "Santiago Giménez", "Raúl Jiménez", "Orbelín Pineda", "Hirving Lozano", "Carlos Rodríguez"],
            "CAN": ["Alphonso Davies", "Jonathan David", "Stephen Eustáquio", "Tajon Buchanan", "Cyle Larin", "Alistair Johnston", "Kamal Miller", "Ismaël Koné"],
            "ARG": ["Lionel Messi", "Lautaro Martínez", "Julian Alvarez", "Emiliano Martínez", "Cristian Romero", "Rodrigo De Paul", "Enzo Fernández", "Alexis Mac Allister", "Angel Di Maria"],
            "BRA": ["Gabriel Magalhães", "Vinicius Junior", "Marquinhos", "Alisson", "Danilo", "Casemiro", "Bruno Guimarães", "Lucas Paquetá", "Rodrygo", "Neymar Jr"],
            "ENG": ["Harry Kane", "Jude Bellingham", "Bukayo Saka", "Jordan Pickford", "Kyle Walker", "John Stones", "Declan Rice", "Phil Foden", "Marcus Rashford"],
            "FRA": ["Kylian Mbappé", "Antoine Griezmann", "Mike Maignan", "Theo Hernandez", "William Saliba", "Eduardo Camavinga", "Aurélien Tchouaméni", "Ousmane Dembélé", "Olivier Giroud"],
            "ESP": ["Lamine Yamal", "Rodri", "Unai Simón", "Dani Carvajal", "Robin Le Normand", "Pedri", "Gavi", "Nico Williams", "Álvaro Morata"],
            "GER": ["Joshua Kimmich", "Marc-André ter Stegen", "Antonio Rüdiger", "Jonathan Tah", "Felix Nmecha", "Leon Goretzka", "Florian Wirtz", "Serge Gnabry", "Kai Havertz", "Leroy Sané"],
            "POR": ["Cristiano Ronaldo", "Bruno Fernandes", "Bernardo Silva", "Rúben Dias", "Rafael Leão"]
        }

        count = 0
        
        # 1. Sync Panini specific stickers
        for tla, players in panini_teams.items():
            team_name = tla 
            print(f"Syncing Panini players for {team_name}...")
            
            # Add Team Badge
            badge_code = f"{tla} 1"
            if not Sticker.query.filter_by(paniniCode=badge_code).first():
                badge = Sticker(
                    name=f"{team_name} Badge",
                    category="Badge",
                    rarity="Rare",
                    team=team_name,
                    paniniCode=badge_code,
                    raretyCatId=rarity_map["Rare"]
                )
                db.session.add(badge)
                count += 1

            for idx, p_name in enumerate(players):
                p_code = f"{tla} {idx + 2}" # Players start at 2
                if not Sticker.query.filter_by(paniniCode=p_code).first():
                    rarity = "Common"
                    if p_name in ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Neymar Jr", "Lamine Yamal"]:
                        rarity = "Legendary"
                    elif p_name in ["Vinicius Junior", "Jude Bellingham", "Harry Kane", "Erling Haaland", "Rodri"]:
                        rarity = "Epic"
                    
                    st = Sticker(
                        name=p_name,
                        category="Player",
                        rarity=rarity,
                        team=team_name,
                        paniniCode=p_code,
                        raretyCatId=rarity_map[rarity]
                    )
                    db.session.add(st)
                    count += 1
            
            # Add Team Photo
            photo_code = f"{tla} 20"
            if not Sticker.query.filter_by(paniniCode=photo_code).first():
                photo = Sticker(
                    name=f"{team_name} Team Photo",
                    category="Team",
                    rarity="Rare",
                    team=team_name,
                    paniniCode=photo_code,
                    raretyCatId=rarity_map["Rare"]
                )
                db.session.add(photo)
                count += 1
        
        db.session.commit()

        # 2. Sync from external API if available
        service = FootballDataService()
        teams_data = service.get_teams()
        
        for team in teams_data.get('teams', []):
            team_name = team.get('name')
            team_id = team.get('id')
            print(f"Syncing players for {team_name} from API...")
            
            squad_data = service.get_team_players(team_id)
            for player in squad_data.get('squad', []):
                player_name = player.get('name')
                
                # Check if sticker already exists (either by name or panini code)
                existing = Sticker.query.filter_by(name=player_name, team=team_name).first()
                if not existing:
                    import random
                    r = random.random()
                    if r < 0.01:
                        rarity = "Legendary"
                    elif r < 0.05:
                        rarity = "Epic"
                    elif r < 0.20:
                        rarity = "Rare"
                    else:
                        rarity = "Common"
                        
                    st = Sticker(
                        name=player_name,
                        category="Player",
                        rarity=rarity,
                        team=team_name,
                        raretyCatId=rarity_map[rarity]
                    )
                    db.session.add(st)
                    count += 1
            
            db.session.commit()
        
        print(f"Sync complete. Added {count} new stickers.")

if __name__ == "__main__":
    sync_stickers()
