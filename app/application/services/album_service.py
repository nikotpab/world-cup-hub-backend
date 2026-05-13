from typing import Dict, Any, List
import random
from datetime import datetime, date
from app.infrastructure.database import db
from app.domain.models.album import Album
from app.domain.models.pack import Pack
from app.domain.models.sticker import Sticker

class AlbumService:
    def __init__(self):
        pass

    def get_user_album(self, user_id: int) -> Dict[str, Any]:
        # 1. Obtener el album del usuario (o crearlo si no existe)
        album = Album.query.filter_by(userId=user_id).first()
        if not album:
            album = Album(userId=user_id)
            db.session.add(album)
            db.session.commit()
            
        # 2. Contar stickers únicos y repetidos en su inventario actual.
        # Por simplicidad del MVP, diremos que todos los stickers obtenidos
        # se añaden directamente al inventario (lista de relaciones).
        
        # Necesitamos todos los stickers que ha obtenido en sus packs.
        packs = Pack.query.filter_by(userId=user_id).all()
        
        all_stickers = []
        for p in packs:
            all_stickers.extend(p.stickers)
            
        unique_stickers = set([s.stickerId for s in all_stickers])
        repeated_stickers_count = len(all_stickers) - len(unique_stickers)
        
        # Max stickers en el álbum
        total_available = Sticker.query.count() or 600
        
        # Lógica de colecciones
        # Agrupar stickers por equipo
        collections_map = {}
        for s in all_stickers:
            team_name = s.team
            if team_name not in collections_map:
                collections_map[team_name] = set()
            collections_map[team_name].add(s.stickerId)
            
        collections_list = []
        i = 1
        for team, unique_s in collections_map.items():
            collections_list.append({
                "id": i,
                "name": team,
                "count": len(unique_s)
            })
            i += 1
            
        # Para que no salga vacío si es nuevo:
        if not collections_list:
            collections_list = [
                {"id": 1, "name": "Selección Argentina"},
                {"id": 2, "name": "Selección Brasil"},
                {"id": 3, "name": "Selección Francia"}
            ]

        completion_percentage = 0
        if total_available > 0:
            completion_percentage = int((len(unique_stickers) / total_available) * 100)

        return {
            "completion_percentage": completion_percentage,
            "total_stickers": len(unique_stickers),
            "max_stickers": total_available,
            "repeated_stickers": repeated_stickers_count,
            "collections": collections_list
        }

    def open_pack(self, user_id: int) -> Dict[str, Any]:
        # Verificar que no haya abierto un paquete hoy
        today = date.today()
        # Buscar packs abiertos por el usuario donde la fecha sea hoy
        packs = Pack.query.filter_by(userId=user_id).all()
        for p in packs:
            if p.openedAt.date() == today:
                raise ValueError("Solo puedes abrir un sobre de láminas al día.")
                
        # Simular la obtención de 5 láminas aleatorias
        # Para evitar problemas si la BD está vacía, creamos algunos stickers temporales
        total_stickers = Sticker.query.count()
        if total_stickers < 5:
            # Crear 50 stickers de prueba si no hay
            for idx in range(1, 51):
                st = Sticker(category="Player", name=f"Player {idx}", rarity="Common", team=f"Team {idx % 5}", raretyCatId=1)
                db.session.add(st)
            db.session.commit()
            
        all_stickers = Sticker.query.all()
        obtained_stickers = random.choices(all_stickers, k=5)
        
        # Registrar el Pack
        new_pack = Pack(
            userId=user_id,
            openedAt=datetime.utcnow()
        )
        for st in obtained_stickers:
            new_pack.stickers.append(st)
            
        db.session.add(new_pack)
        db.session.commit()
        
        return {
            "success": True,
            "message": "¡Has abierto un sobre con éxito!",
            "stickers": [{"id": s.stickerId, "name": s.name, "team": s.team} for s in obtained_stickers]
        }
