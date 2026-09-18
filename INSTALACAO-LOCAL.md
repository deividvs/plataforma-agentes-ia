# Instalação local CDC Agentes

Repositório: https://github.com/deividvs/plataforma-agentes-ia
Commit inicial: `4f630b7`. Ambiente: macOS, Python 3.12.13, Node 22.12.0.

## Estado da instalação

- Dependências instaladas em `.venv` e `frontend/node_modules`; lockfile do frontend atualizado para corrigir a auditoria de segurança.
- TypeScript e build do frontend passaram. Artefatos em `frontend/build`.
- Verificação `tools/security_check.py` e `pip check` passaram.
- Tela de login validada no navegador, sem erros de console; captura em `var/logs/login.png`.
- Redis próprio: container `cdc-agentes-redis-1`, porta local 6380, volume persistente `cdc-agentes_redis_data`; health e PING passaram.
- Supabase CENTRAL (`kcpbemdzalwzvdjgpjlg`): schema privado `cdc_agentes` com migrations `0001` e `0002` (auditoria de webhooks). Sem acesso para `anon` e `authenticated`. As 21 tabelas existentes em `public` foram preservadas.
- Uma empresa e uma conta administradora ativa foram criadas. O e-mail cadastrado é `deivid.dvs@gmail.com`; use a senha definida durante o cadastro.
- API, worker Celery, beat e painel iniciados localmente. A API e o painel responderam HTTP 200; o login com conta inexistente retornou HTTP 400 nos dois caminhos, confirmando o proxy e o acesso ao banco.
- WAHA CORE em `cdc-agentes-waha-1`, imagem ARM nativa `devlikeapro/waha:noweb-arm`, porta local 3000, sessões no volume `cdc-agentes_waha_sessions`. A empresa 1 tem uma sessão NOWEB em `SCAN_QR_CODE`; conexão, início da sessão e consulta do QR pelo painel responderam HTTP 200. Eventos recebidos foram gravados em `webhook_audit`.
- Chave OpenAI recuperada de `meu-primeiro-agente/.env`, validada com os modelos exigidos e salva criptografada para a empresa 1 no Supabase. A criação de agentes já pode usar essa credencial.
- Falta vincular um telefone pelo QR code. SMTP e Google Calendar seguem sem configuração.

## Conexão e conclusão

`backend/.env` já contém a URI do CENTRAL, `DATABASE_SCHEMA=cdc_agentes` e `PGSSLMODE=require`. O arquivo tem permissão 600. Mantenha a senha fora do Git. Caracteres especiais na senha da URI precisam ser codificados como percent-encoding. A aplicação aplica `SET LOCAL search_path` no início de cada transação, pois o pooler do Supabase pode trocar a conexão física após um commit.

O gerenciador local carrega o `.env`, normaliza o driver para psycopg2 e prepara o ambiente dos serviços:

```bash
.venv/bin/python tools/local_services.py migrate
.venv/bin/python tools/local_services.py check-db
.venv/bin/python tools/local_services.py start
.venv/bin/python tools/local_services.py status
.venv/bin/python tools/local_services.py stop
```

Antes de futuras migrations, confirme que a conexão usa CENTRAL e `current_schema()` retorna `cdc_agentes`. O primeiro administrador já foi criado; não há senha padrão. Para entrar, acesse http://127.0.0.1:3004/login com o e-mail acima e a senha informada no bootstrap.

O worker usa pool `solo`, adequado ao teste local no macOS. A reserva de conexões para operações de login (`IDENTITY_OPERATION_POOL_HEADROOM=12`) acompanha o pool local de 20 conexões. O Colima precisa estar ativo para manter Redis e WAHA disponíveis; use `colima start` se ele estiver parado. Os processos Python não estão registrados para iniciar no login/reboot.

## Iniciar o painel, Redis e WAHA

```bash
colima start
docker compose -p cdc-agentes --env-file .env.dependencies -f compose.dependencies.yml up -d redis waha
.venv/bin/python tools/local_services.py start
npm --prefix frontend start
```

Painel: http://127.0.0.1:3004. API: http://127.0.0.1:8002. WAHA: http://127.0.0.1:3000/dashboard.
Inicie somente `redis waha` no Compose; o banco escolhido é Supabase. As credenciais do Dashboard estão em `.env.waha` (permissão 600); a chave de API em texto simples fica apenas em `backend/.env` (permissão 600), e o container recebe seu hash SHA-512.

A API escuta em `0.0.0.0:8002` para receber webhooks do container. O WAHA usa `http://host.docker.internal:8002/webhook/waha/callback`, e esse host está incluído em `ALLOWED_HOSTS`. No painel, abra a conexão WhatsApp para criar a sessão da empresa e escaneie o QR code com o telefone. O webhook é configurado pela aplicação ao criar a sessão. Consulte a [instalação oficial do WAHA](https://waha.devlike.pro/docs/how-to/install/) e a [configuração de chave de API](https://waha.devlike.pro/docs/how-to/security/).

O fluxo de conexão foi corrigido para não referenciar colunas legadas do WPPConnect ausentes da tabela `companies`. A migration `0002` adiciona `webhook_audit`, usada pelo recebimento e pela deduplicação de eventos. Após uma falha de disco, o volume WAHA contendo apenas uma sessão não pareada foi recriado; caches reconstruíveis de uv, modelos Hugging Face e atualização do VS Code foram removidos para liberar espaço.

O validador OpenAI em `backend/services/ai_provider_service.py` usa 16 tokens no teste mínimo, pois a API rejeitou o limite anterior de 1 token. A credencial da empresa 1 foi verificada e armazenada criptografada; o valor também está em `backend/.env` para módulos legados.

## Correções da auditoria de dependências

Atualização autorizada após a instalação inicial:

| Pacote | Antes | Depois |
| --- | --- | --- |
| browserslist | 4.28.5 | 4.29.0 |
| baseline-browser-mapping | 2.10.42 | 2.11.25 |
| nanoid | 3.3.16 | 3.3.19 |
| deepmerge-ts | 7.1.5 | 8.0.2 |

As bases auxiliares do Browserslist também foram atualizadas. Flowbite React permanece em 0.12.17, com override restrito de `deepmerge-ts` para 8.0.2. A versão publicada do Flowbite ainda fixa 7.1.5; revisar a necessidade desse override quando o pacote incorporar a correção.

O changelog de deepmerge-ts 8 descreve mudanças em Maps, deepmergeInto e tipos internos. O Flowbite utiliza deepmerge e deepmergeCustom para temas. Foram verificados merge de classes, temas aninhados, preservação dos objetos de entrada e renderização de Button, Alert, Badge, Select e Spinner.

Referência: https://github.com/RebeccaStevens/deepmerge-ts/blob/main/CHANGELOG.md

A reinstalação com `npm ci` passou, com zero vulnerabilidades reportadas. `psutil==6.1.1` foi incluído em `backend/requirements.txt` após uma falha de importação na inicialização da API. `pip check` passou. A autenticação com a senha real deve ser confirmada pelo titular da conta.
