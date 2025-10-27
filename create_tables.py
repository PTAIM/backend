"""
Script para criar todas as tabelas no banco de dados.
Execute este arquivo para inicializar o banco de dados.
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importa o Base e engine
from app.core.database import Base, engine

# Importa todos os modelos para que sejam registrados no Base.metadata
from app.gestao_perfis.models import (
    Usuario, 
    Paciente, 
    Medico, 
    Especialidade, 
    MedicoEspecialidade, 
    Agenda, 
    SumarioSaude
)

# Importar modelos de gestão de consultas
from app.gestao_consultas.models import Consulta, LogProntuario

# Importar modelos de gestão de exames
from app.gestao_exames.models import SolicitacaoExame, ResultadoExame, Laudo, LaudoResultado


def main():
    print("🔨 Criando tabelas no banco de dados...")
    print(f"📊 Database URL: {engine.url}")
    
    try:
        # Cria todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("\n✅ Tabelas criadas com sucesso!")
        
        # Lista as tabelas criadas
        print("\n📋 Tabelas criadas:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
            
    except Exception as e:
        print(f"\n❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
