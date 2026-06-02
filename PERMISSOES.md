# Permissões dos Usuários — Sistema de Agendamento de Veículos

## Mecanismo de Autorização

O sistema usa **Django Groups** (`auth.Group`) como mecanismo central de autorização.  
Cada usuário pertence a um grupo, e os métodos `is_X()` no model `Usuario` consultam esse grupo.

```python
# usuarios/models.py
def is_administrador(self):
    return self.is_superuser or self.groups.filter(name='Administradores').exists()

def is_professor(self):
    return self.groups.filter(name='Professores').exists()

def is_motorista(self):
    return self.groups.filter(name='Motoristas').exists()

def is_responsavel_campus(self):
    return self.groups.filter(name='Responsaveis de Campus').exists()
```

---

## Grupos Existentes

| Grupo | Como é criado |
|---|---|
| `Administradores` | Manualmente via Django Admin ou superuser |
| `Professores` | Automaticamente ao se registrar em `/usuarios/registro/` |
| `Motoristas` | Criado por Responsável de Campus em `/usuarios/motoristas/novo/` |
| `Responsaveis de Campus` | Manualmente via Django Admin |

> **Superusuário** (`is_superuser=True`) também passa na verificação `is_administrador()`, mesmo sem estar no grupo.

---

## Matriz de Acesso por Grupo

### Administrador

| Área | Acesso |
|---|---|
| **Campi** — listar, criar, editar, excluir | ✅ Total |
| **Cursos** — listar, criar, editar, excluir | ✅ Total |
| **Veículos** — listar, criar, editar, excluir | ✅ Total |
| **Agendamentos** — aprovar, reprovar | ✅ Todos os campi |
| **Agendamentos** — relatório geral, por curso, por professor | ✅ Todos os campi |
| **Agendamentos** — exportar Excel/PDF | ✅ Todos os campi |
| **Motoristas** — listar, criar, editar, desativar | ✅ Todos os campi |
| **Abastecimentos** — listar, criar, editar, excluir | ✅ Todos |
| **Ocorrências** — listar, criar, editar, excluir, resolver | ✅ Todas |
| **Boletim Diário** | ✅ Todos os veículos |
| **Dashboard** | Calendário geral (todos os agendamentos exceto reprovados) |
| **Django Admin** (`/admin/`) | ✅ Acesso completo |

---

### Responsável de Campus

Mesmas permissões do Administrador, **mas os dados são filtrados pelo campus vinculado ao usuário** (`usuario.campus`).

| Área | Acesso |
|---|---|
| **Campi** — CRUD | ❌ Sem acesso (exclusivo do Admin) |
| **Cursos** — listar, criar, editar, excluir | ✅ Apenas do próprio campus (`curso.campus = usuario.campus`) |
| **Veículos** — listar, criar, editar, excluir | ✅ Apenas do próprio campus (`veiculo.campus = usuario.campus`) |
| **Agendamentos** — aprovar, reprovar | ✅ Apenas do próprio campus (`professor__campus = usuario.campus`) |
| **Agendamentos** — relatório geral | ✅ Filtrado pelo campus |
| **Agendamentos** — relatório por professor | ✅ Professores do campus |
| **Agendamentos** — exportar Excel/PDF | ✅ Filtrado pelo campus |
| **Motoristas** — listar, criar, editar, desativar | ✅ Gerencia motoristas |
| **Abastecimentos** — listar, ver, editar, excluir | ✅ Todos |
| **Ocorrências** — listar, ver, editar, excluir, resolver | ✅ Todas |
| **Boletim Diário** | ✅ Todos os veículos |
| **Dashboard** | Redireciona para `/frotas/responsavel/` |

> O campo `campus` é obrigatório no cadastro do Responsável (feito via Django Admin).

---

### Professor

| Área | Acesso |
|---|---|
| **Calendário / Dashboard** | ✅ Vê todos os agendamentos aprovados + os próprios pendentes |
| **Agendamentos** — criar | ✅ |
| **Agendamentos** — editar / cancelar | ✅ Apenas os próprios, enquanto `status='pendente'` |
| **Agendamentos** — aprovar / relatórios | ❌ |
| **Campi / Cursos / Veículos** | ❌ |
| **Frotas (abastecimento, ocorrência)** | ❌ |
| **Perfil** | ✅ Editar próprios dados |

> **Registro automático:** ao criar conta em `/usuarios/registro/`, o usuário é adicionado ao grupo `Professores` automaticamente.

---

### Motorista

| Área | Acesso |
|---|---|
| **Dashboard Motorista** (`/frotas/motorista/`) | ✅ |
| **Abastecimentos** — criar | ✅ |
| **Abastecimentos** — listar / ver / editar / excluir | ✅ Apenas os próprios |
| **Ocorrências** — criar | ✅ |
| **Ocorrências** — listar / ver / editar / excluir | ✅ Apenas as próprias |
| **Ocorrências** — resolver | ❌ Exclusivo de Admin / Responsável |
| **Calendário / Agendamentos** | ❌ |
| **Boletim Diário / Relatórios** | ❌ |

> **Criação:** motoristas são criados por Responsável de Campus ou Administrador em `/usuarios/motoristas/novo/`. Ficam ativos imediatamente (sem fluxo de e-mail).

---

## Redirecionamentos Pós-Login

Definido em `CustomLoginView.get_success_url()` (`usuarios/views.py`):

```
Motorista        → /frotas/motorista/
Responsável      → /frotas/responsavel/
Administrador    → /  (dashboard)
Professor        → /  (dashboard)
```

---

## Decorators Disponíveis

Definidos em `common/decorators.py`:

| Decorator / Função | Permite acesso |
|---|---|
| `@user_passes_test(is_administrador)` | Apenas Administradores e superusers |
| `@user_passes_test(is_responsavel_ou_admin)` | Responsáveis de Campus **e** Administradores |
| `@responsavel_campus_required` | Responsáveis de Campus **e** Administradores (com mensagem de erro customizada) |
| `@motorista_required` | Apenas Motoristas |
| `@administrador_required` | Apenas Administradores e superusers (com mensagem customizada) |
| `@login_required` | Qualquer usuário autenticado |

---

## Quem Usa Cada Decorator

### `@user_passes_test(is_administrador)` — somente admin

| View | Arquivo |
|---|---|
| `lista_campi`, `criar_campus`, `editar_campus`, `deletar_campus` | `campus/views.py` |

### `@user_passes_test(is_responsavel_ou_admin)` — responsável + admin

| View | Arquivo |
|---|---|
| `lista_cursos`, `criar_curso`, `editar_curso`, `deletar_curso` | `cursos/views.py` |
| `lista_veiculos`, `criar_veiculo`, `editar_veiculo`, `deletar_veiculo` | `veiculos/views.py` |
| `aprovacao_agendamentos`, `aprovar_agendamento`, `reprovar_agendamento` | `agendamentos/views/aprovacao_views.py` |
| `relatorio_geral`, `relatorio_por_curso`, `relatorio_por_professor` | `agendamentos/views/relatorio_views.py` |
| `exportar_relatorio_excel`, `exportar_relatorio_pdf` | `agendamentos/views/export_views.py` |
| `exportar_curso_excel` | `agendamentos/views/export_views.py` |
| `exportar_professor_excel`, `exportar_professor_pdf` | `agendamentos/views/export_views.py` |

### `@responsavel_campus_required` — responsável + admin

| View | Arquivo |
|---|---|
| `lista_motoristas`, `criar_motorista`, `editar_motorista`, `desativar_motorista` | `usuarios/views.py` |

### `@login_required` com verificação manual interna — qualquer autenticado

| View | Lógica interna |
|---|---|
| `lista_abastecimentos` | Admin/Resp. vê todos; Motorista vê apenas os próprios |
| `criar_abastecimento` | Qualquer autenticado; motorista é definido automaticamente |
| `detalhe/editar/deletar_abastecimento` | Owner **ou** Admin/Resp. |
| `lista_ocorrencias` | Admin/Resp. vê todas; Motorista vê apenas as próprias |
| `criar_ocorrencia` | Qualquer autenticado |
| `detalhe/editar/deletar_ocorrencia` | Owner **ou** Admin/Resp. |
| `resolver_ocorrencia` | Apenas Admin ou Resp. (verificado internamente) |
| `boletim_diario` | Verificado internamente: Admin ou Resp. |
| `dashboard_motorista` | Verificado internamente: `is_motorista()` |
| `dashboard_responsavel` | Verificado internamente: `is_responsavel_campus()` ou `is_administrador()` |

---

## Filtragem por Campus (Responsável)

Quando `request.user.is_responsavel_campus()` é `True` e o usuário **não** é administrador, os seguintes querysets são filtrados automaticamente:

| View | Filtro aplicado |
|---|---|
| `lista_cursos` | `.filter(campus=request.user.campus)` |
| `editar_curso` / `deletar_curso` | Bloqueia se `curso.campus != usuario.campus` |
| `lista_veiculos` | `.filter(campus=request.user.campus)` |
| `editar_veiculo` / `deletar_veiculo` | Bloqueia se `veiculo.campus != usuario.campus` |
| `aprovacao_agendamentos` | `.filter(professor__campus=request.user.campus)` |
| `relatorio_geral` | `.filter(professor__campus=request.user.campus)` |
| `relatorio_por_professor` | `professores.filter(campus=request.user.campus)` |
| `exportar_relatorio_excel` | `.filter(professor__campus=request.user.campus)` |
| `exportar_relatorio_pdf` | `.filter(professor__campus=request.user.campus)` |
