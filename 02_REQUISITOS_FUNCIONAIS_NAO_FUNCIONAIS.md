# 02 — Requisitos funcionais e não funcionais

## 1. Prioridades

- **P0:** indispensável para provar o MVP.
- **P1:** importante para uma versão utilizável.
- **P2:** evolução posterior.

## 2. Requisitos funcionais

| ID | Requisito | Prioridade |
|---|---|---|
| RF-001 | Criar e salvar projetos de personagem | P0 |
| RF-002 | Armazenar a identidade do personagem em `CharacterSpec` | P0 |
| RF-003 | Montar personagem a partir de componentes 3D compatíveis | P0 |
| RF-004 | Aplicar perfil artístico e materiais definidos | P0 |
| RF-005 | Associar personagem a uma família de rig | P0 |
| RF-006 | Executar idle, walk e run | P0 |
| RF-007 | Renderizar oito direções | P0 |
| RF-008 | Renderizar PNG com transparência | P0 |
| RF-009 | Gerar metadados de animação e atlas | P0 |
| RF-010 | Validar existência, dimensões e integridade dos arquivos | P0 |
| RF-011 | Exportar pacote consumível por Godot | P0 |
| RF-012 | Mostrar o progresso de jobs | P1 |
| RF-013 | Manter histórico de versões | P1 |
| RF-014 | Permitir comparação visual entre versões | P1 |
| RF-015 | Gerar concept art com provider de IA | P1 |
| RF-016 | Converter prompt em proposta de `CharacterSpec` | P1 |
| RF-017 | Permitir aprovação/rejeição de conceito | P1 |
| RF-018 | Permitir regeneração seletiva de etapas | P1 |
| RF-019 | Biblioteca pesquisável de componentes | P1 |
| RF-020 | Geração em lote | P2 |
| RF-021 | Famílias de quadrúpedes e criaturas | P2 |
| RF-022 | Providers locais e remotos intercambiáveis | P1 |
| RF-023 | Relatório de origem e licença dos assets | P1 |

## 3. Requisitos não funcionais

| ID | Requisito | Critério/observação |
|---|---|---|
| RNF-001 | Reprodutibilidade | Mesmas entradas e versões devem permitir reproduzir o processo dentro das limitações do ambiente |
| RNF-002 | Modularidade | Módulos devem ter contratos explícitos e dependências controladas |
| RNF-003 | Recuperação | Falha em uma etapa não deve apagar resultados válidos anteriores |
| RNF-004 | Rastreabilidade | Jobs registram inputs, versões, logs e outputs |
| RNF-005 | Segurança local | Backend local não deve ficar exposto à rede sem configuração explícita |
| RNF-006 | Usabilidade | Operações longas mostram progresso, estado e erro compreensível |
| RNF-007 | Portabilidade futura | Separar regras de negócio da interface e do sistema operacional |
| RNF-008 | Qualidade visual | Câmera, escala, luz, pivô e perfil artístico padronizados |
| RNF-009 | Integridade de exportação | Manifest deve corresponder aos arquivos realmente produzidos |
| RNF-010 | Licenciamento | Registrar origem e licença dos modelos, texturas, fontes e modelos de IA usados |
| RNF-011 | Testabilidade | Operações centrais devem poder ser executadas por CLI/testes automatizados |
| RNF-012 | Observabilidade | Logs estruturados por projeto, job e etapa |

## 4. Requisitos de desempenho — metas a medir

As metas quantitativas definitivas ainda não estão aprovadas. Durante o MVP, medir:

- tempo para montar a cena do personagem;
- tempo de render por frame;
- tempo total por animação e por oito direções;
- memória máxima durante renderização;
- tamanho dos arquivos de saída;
- taxa de falhas por etapa.

Não definir limites rígidos antes de executar o primeiro benchmark com a máquina-alvo e a resolução de produção.

## 5. Regras de negócio

- Um personagem deve estar associado a uma família de rig.
- Um componente deve declarar compatibilidade e pontos de ancoragem.
- Animações só podem ser aplicadas a rigs compatíveis ou a rigs com retargeting validado.
- Uma exportação só pode ser marcada como concluída depois da validação dos arquivos.
- Um conceito de IA não se torna automaticamente o modelo final.
- Uma alteração de aparência deve produzir uma nova revisão ou versão rastreável.
- A direção do personagem deve ser renderizada a partir da cena 3D, não simulada por espelhamento de imagens.
