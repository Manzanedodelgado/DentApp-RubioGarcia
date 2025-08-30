#!/usr/bin/env python3
"""
Configurar OAuth2 para acceso con tu cuenta personal
Más fácil que Service Account para este caso
"""

import gspread
from google.auth import default
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json

def setup_oauth_user_credentials():
    """
    Configurar OAuth para usar tu cuenta personal
    """
    print("🔧 CONFIGURACIÓN OAUTH2 PARA CUENTA PERSONAL")
    print("=" * 60)
    
    # Crear archivo credentials.json temporal
    client_config = {
        "web": {
            "client_id": "116210132025620008395-compute@developer.gserviceaccount.com",
            "project_id": "appgest-470518",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_secret": "GOCSPX-fake-for-service-account"
        }
    }
    
    print("🚨 IMPORTANTE: Necesitamos crear OAuth Client ID")
    print("\n📋 PASOS MANUALES NECESARIOS:")
    print("1. Ve a: https://console.cloud.google.com/apis/credentials")
    print("2. Clic '+ CREATE CREDENTIALS' → 'OAuth client ID'")
    print("3. Application type: 'Desktop application'")
    print("4. Name: 'Gesden Sync Desktop'")
    print("5. Clic 'Create'")
    print("6. DESCARGAR el archivo JSON")
    print("7. Renombrarlo a: 'oauth_credentials.json'")
    print("8. Ponerlo en la misma carpeta que este script")
    
    return False

def test_oauth_user_access():
    """
    Probar acceso con OAuth user credentials
    """
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    creds = None
    # El archivo token.json guarda los tokens de acceso y refresh del usuario.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas disponibles, permite al usuario autenticar.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('oauth_credentials.json'):
                print("❌ ERROR: No se encontró oauth_credentials.json")
                print("   Sigue los pasos arriba para crearlo")
                return False
            
            flow = Flow.from_client_secrets_file(
                'oauth_credentials.json', SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print(f"🌐 Ve a esta URL para autorizar: {auth_url}")
            code = input('Pega el código de autorización aquí: ')
            
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        # Guardar las credenciales para la próxima ejecución
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Probar acceso
    try:
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key('1MBDBHQ08XGuf5LxVHCFhHDagIazFkpBnxwqyEQIBJrQ').sheet1
        
        # Probar escritura
        test_row = [f"OAUTH-TEST-{int(datetime.datetime.now().timestamp())}", "Test OAuth", "Write access"]
        sheet.append_row(test_row)
        
        print("✅ OAuth User Access funciona perfectamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error con OAuth: {e}")
        return False

if __name__ == "__main__":
    import datetime
    
    print("🔧 CONFIGURADOR OAUTH PARA GOOGLE SHEETS")
    print("Esto te dará acceso de escritura usando TU cuenta personal")
    print()
    
    if os.path.exists('oauth_credentials.json'):
        print("✅ Encontrado oauth_credentials.json")
        success = test_oauth_user_access()
        if success:
            print("\n🎉 ¡LISTO! Ahora puedes usar sync_modified.py")
    else:
        setup_oauth_user_credentials()