"""Configura o funil comercial inicial sem alterar funis já personalizados.

Uso: .venv/bin/python tools/setup_commercial_pipeline.py --company-id 1
"""

import argparse
import os
from pathlib import Path
import sys

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.update({key: value for key, value in dotenv_values(ROOT / "backend/.env").items() if value is not None})

from backend.db import SessionLocal
from backend.models import Pipeline, PipelineStage


STAGES = (
    ("Contato iniciado", "Primeira abordagem enviada; aguarda resposta do lead.", "#2563EB", False, False),
    ("Qualificado", "Necessidade e perfil confirmados; há oportunidade comercial.", "#0891B2", False, False),
    ("Proposta enviada", "Oferta e condições apresentadas ao lead.", "#7C3AED", False, False),
    ("Negociação", "Proposta em discussão; preço, prazo ou escopo em ajuste.", "#D97706", False, False),
    ("Ganhou", "Oportunidade fechada com sucesso.", "#16A34A", True, False),
    ("Perdido", "Oportunidade encerrada sem venda.", "#DC2626", False, True),
)


def setup(company_id: int) -> None:
    with SessionLocal() as db:
        pipeline = (
            db.query(Pipeline)
            .filter(Pipeline.company_id == company_id, Pipeline.is_active.is_(True))
            .order_by(Pipeline.id)
            .first()
        )
        if pipeline is None:
            raise SystemExit(f"Empresa {company_id}: pipeline ativo não encontrado")

        stages = (
            db.query(PipelineStage)
            .filter(PipelineStage.pipeline_id == pipeline.id)
            .order_by(PipelineStage.order, PipelineStage.id)
            .all()
        )
        if len(stages) != 1 or not stages[0].is_first_stage:
            print("Pipeline já personalizado; nenhuma etapa foi alterada")
            return

        first = stages[0]
        first.name = "Novo Lead"
        first.description = "Lead captado, ainda sem abordagem comercial."
        first.color = "#64748B"
        first.order = first.order_index = 1
        first.percentage_base_stage_id = None

        previous = first
        for order, (name, description, color, converted, lost) in enumerate(STAGES, start=2):
            stage = PipelineStage(
                pipeline_id=pipeline.id,
                name=name,
                description=description,
                color=color,
                order=order,
                order_index=order,
                is_first_stage=False,
                is_converted_stage=converted,
                is_lost_stage=lost,
                percentage_base_stage_id=first.id if lost else previous.id,
            )
            db.add(stage)
            db.flush()
            if not lost:
                previous = stage

        db.commit()
        print(f"Pipeline {pipeline.id}: {len(STAGES) + 1} etapas comerciais configuradas")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company-id", type=int, required=True)
    setup(parser.parse_args().company_id)
