# Pipeline comercial

O pipeline principal da empresa 1 no Supabase CENTRAL usa estas etapas, nesta ordem:

| Etapa | Critério de entrada | Base da conversão |
| --- | --- | --- |
| Novo Lead | Contato captado, ainda sem abordagem | Leads captados |
| Contato iniciado | Primeira abordagem enviada | Novo Lead |
| Qualificado | Necessidade e perfil confirmados | Contato iniciado |
| Proposta enviada | Oferta e condições apresentadas | Qualificado |
| Negociação | Proposta em discussão | Proposta enviada |
| Ganhou | Oportunidade fechada com sucesso | Negociação |
| Perdido | Oportunidade encerrada sem venda | Novo Lead |

**Métricas do painel:** “Em etapa” conta os leads captados no intervalo selecionado que estão atualmente nessa etapa; “Alcançaram” conta cada lead da mesma coorte uma vez por etapa, usando o histórico de movimentação; “Conversão” é `Leads que alcançaram esta etapa e a etapa base ÷ Leads que alcançaram a etapa base × 100`. Isso mantém a taxa correta mesmo quando uma movimentação pula etapas. “Perdido” é um desfecho alternativo, por isso sua base é Novo Lead. Os leads captados no período formam a entrada do funil, e “Novo Lead” é essa mesma entrada, sem uma linha duplicada.

O painel também exibe **Vendas** e **Faturamento**, vindos dos registros financeiros de venda. São eventos distintos do status “Ganhou” no CRM: mover um lead para “Ganhou” não cria automaticamente uma venda. A razão “Vendas / Leads” do painel principal compara eventos do mesmo intervalo, mas não é uma taxa de conversão por coorte; para analisar avanço do CRM, use “Alcançaram” e “Conversão” na tabela de etapas.

Não há leads históricos nessa empresa neste momento, portanto ainda não existe base real para definir metas ou tempos esperados por etapa. O configurador `tools/setup_commercial_pipeline.py` só aplica a sequência inicial quando o pipeline contém exclusivamente a etapa inicial; pipelines personalizados são preservados.
