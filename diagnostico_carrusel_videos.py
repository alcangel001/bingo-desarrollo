"""
Script de diagnóstico para el problema del carrusel de videos
Este script verifica:
1. Si hay anuncios con video_url en la base de datos
2. El formato de las URLs guardadas
3. Si el filtro get_embed_url funciona correctamente
4. El HTML generado
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')
django.setup()

from bingo_app.models import Announcement
from bingo_app.templatetags.bingo_filters import get_embed_url

print("=" * 80)
print("DIAGNÓSTICO DEL CARRUSEL DE VIDEOS")
print("=" * 80)

# 1. Verificar anuncios con video_url
announcements_with_video = Announcement.objects.filter(
    video_url__isnull=False
).exclude(video_url='')

print(f"\n1. Anuncios con video_url encontrados: {announcements_with_video.count()}")

if announcements_with_video.count() > 0:
    for ann in announcements_with_video:
        print(f"\n   Anuncio ID: {ann.id}")
        print(f"   Mensaje: {ann.message[:50]}...")
        print(f"   video_url original: {ann.video_url}")
        print(f"   video_url tipo: {type(ann.video_url)}")
        print(f"   video_url vacío?: {not ann.video_url or ann.video_url == ''}")
        
        # Probar el filtro
        embed_url = get_embed_url(ann.video_url)
        print(f"   URL embed generada: {embed_url}")
        print(f"   URL embed vacía?: {not embed_url or embed_url == ''}")
        print(f"   is_active: {ann.is_active}")
        print(f"   order: {ann.order}")
else:
    print("\n   ⚠️  NO HAY ANUNCIOS CON VIDEO_URL EN LA BASE DE DATOS")
    print("   Esto podría ser el problema principal.")

# 2. Verificar todos los anuncios activos
print(f"\n2. Todos los anuncios activos: {Announcement.objects.filter(is_active=True).count()}")
active_announcements = Announcement.objects.filter(is_active=True).order_by('order')
for ann in active_announcements:
    has_video = bool(ann.video_url)
    has_image = bool(ann.image)
    print(f"   ID {ann.id}: video={has_video}, image={has_image}, message='{ann.message[:30]}...'")

# 3. Probar el filtro con URLs de ejemplo
print("\n3. Pruebas del filtro get_embed_url:")
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://vimeo.com/123456789",
    "https://example.com/video",
]

for url in test_urls:
    result = get_embed_url(url)
    print(f"   Input:  {url}")
    print(f"   Output: {result}")
    print()

print("=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)

