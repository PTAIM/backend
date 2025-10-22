"""
Service para Gestão de Agenda
Feature 1 - Épico 2: Ciclo de Vida de Consultas
"""
from typing import List, Optional
from datetime import time, datetime, timedelta
from sqlalchemy.orm import Session

from app.gestao_perfis.models.agenda import Agenda, DiaSemana


class AgendaService:
    """Service para gerenciar agenda de médicos"""
    
    @staticmethod
    def definir_horario_atendimento(
        db: Session,
        medico_id: int,
        dia_semana: DiaSemana,
        hora: time
    ) -> Agenda:
        """
        História 1.1: Definir horários de atendimento
        Médico define dias e horários recorrentes de atendimento
        """
        # Verifica se horário já existe
        horario_existente = db.query(Agenda).filter(
            Agenda.medicoId == medico_id,
            Agenda.diaSemana == dia_semana,
            Agenda.hora == hora
        ).first()
        
        if horario_existente:
            raise ValueError("Horário já cadastrado para este dia")
        
        # Cria novo horário
        novo_horario = Agenda(
            medicoId=medico_id,
            diaSemana=dia_semana,
            hora=hora
        )
        
        db.add(novo_horario)
        db.commit()
        db.refresh(novo_horario)
        
        return novo_horario
    
    @staticmethod
    def remover_horario_atendimento(
        db: Session,
        agenda_id: int
    ) -> bool:
        """Remove horário de atendimento"""
        horario = db.query(Agenda).filter(Agenda.id == agenda_id).first()
        
        if not horario:
            return False
        
        db.delete(horario)
        db.commit()
        
        return True
    
    @staticmethod
    def listar_horarios_medico(
        db: Session,
        medico_id: int,
        dia_semana: Optional[DiaSemana] = None
    ) -> List[Agenda]:
        """
        História 1.1: Listar horários do médico
        Retorna horários disponíveis do médico
        """
        query = db.query(Agenda).filter(Agenda.medicoId == medico_id)
        
        if dia_semana:
            query = query.filter(Agenda.diaSemana == dia_semana)
        
        return query.all()
    
    @staticmethod
    def obter_horarios_disponiveis(
        db: Session,
        medico_id: int,
        data_inicio: datetime,
        data_fim: datetime
    ) -> List[datetime]:
        """
        História 1.1 e 1.2: Mostrar horários vagos
        Retorna lista de horários disponíveis (sem consulta agendada)
        """
        from app.gestao_consultas.models.consulta import Consulta, StatusConsulta
        
        # Busca agenda do médico
        horarios_agenda = db.query(Agenda).filter(Agenda.medicoId == medico_id).all()
        
        # Gera todos os horários possíveis no período
        horarios_possiveis = []
        data_atual = data_inicio
        
        while data_atual <= data_fim:
            dia_semana_map = {
                0: DiaSemana.SEGUNDA,
                1: DiaSemana.TERCA,
                2: DiaSemana.QUARTA,
                3: DiaSemana.QUINTA,
                4: DiaSemana.SEXTA,
                5: DiaSemana.SABADO,
                6: DiaSemana.DOMINGO
            }
            
            dia_semana = dia_semana_map.get(data_atual.weekday())
            
            # Verifica se médico atende neste dia
            for horario in horarios_agenda:
                if horario.diaSemana == dia_semana:
                    horario_completo = datetime.combine(
                        data_atual.date(),
                        horario.hora
                    )
                    horarios_possiveis.append(horario_completo)
            
            data_atual += timedelta(days=1)
        
        # Remove horários já agendados
        consultas_agendadas = db.query(Consulta).filter(
            Consulta.medicoId == medico_id,
            Consulta.dataHora.between(data_inicio, data_fim),
            Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA])
        ).all()
        
        horarios_ocupados = {c.dataHora for c in consultas_agendadas}
        horarios_disponiveis = [h for h in horarios_possiveis if h not in horarios_ocupados]
        
        return sorted(horarios_disponiveis)
