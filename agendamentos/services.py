"""
Serviços de negócio para agendamentos.

Este módulo contém a lógica de negócio relacionada a agendamentos,
separada das views (Single Responsibility Principle).
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q

from usuarios.models import Usuario


class AgendamentoService:
    """
    Serviço para operações de negócio relacionadas a agendamentos.
    """

    @staticmethod
    def criar_agendamento(form, formset, usuario):
        """
        Cria um novo agendamento com seus trajetos.

        Args:
            form: Form de agendamento validado
            formset: Formset de trajetos validado
            usuario: Usuário que está criando o agendamento

        Returns:
            Agendamento: Objeto criado

        Raises:
            ValidationError: Se houver erro de validação
        """
        # Valida se pelo menos um trajeto foi preenchido
        trajetos_preenchidos = sum(
            1 for f in formset
            if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
        )

        if trajetos_preenchidos < 1:
            raise ValidationError(
                'Adicione pelo menos um trajeto ao agendamento.'
            )

        # Calcula total de KM
        total_km_trajetos = sum(
            f.cleaned_data.get('quilometragem', 0)
            for f in formset
            if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
        )

        # Valida limite de KM
        form.validar_limite_km_manual(total_km_trajetos)

        # Cria o agendamento com transaction
        with transaction.atomic():
            agendamento = form.save(commit=False)
            agendamento.professor = usuario
            agendamento.status = 'pendente'
            agendamento.save()

            # Salva os trajetos
            formset.instance = agendamento
            formset.save()

        return agendamento

    @staticmethod
    def editar_agendamento(form, formset, agendamento):
        """
        Edita um agendamento existente.

        Args:
            form: Form de agendamento validado
            formset: Formset de trajetos validado
            agendamento: Agendamento a ser editado

        Returns:
            Agendamento: Objeto atualizado

        Raises:
            ValidationError: Se houver erro de validação
        """
        # Calcula total de KM
        total_km_trajetos = sum(
            f.cleaned_data.get('quilometragem', 0)
            for f in formset
            if f.cleaned_data and not f.cleaned_data.get('DELETE', False)
        )

        # Valida limite de KM
        form.validar_limite_km_manual(total_km_trajetos)
        
        # Valida se os trajetos estão dentro do período do agendamento
        # usando os dados NOVOS do formulário (não os dados antigos do banco)
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        
        for trajeto_form in formset:
            if not trajeto_form.cleaned_data:
                continue
            if trajeto_form.cleaned_data.get('DELETE', False):
                continue
                
            data_saida = trajeto_form.cleaned_data.get('data_saida')
            data_chegada = trajeto_form.cleaned_data.get('data_chegada')
            
            if data_saida and data_inicio and data_saida < data_inicio:
                data_fmt = data_inicio.strftime("%d/%m/%Y %H:%M")
                raise ValidationError(
                    f'A data de saída do trajeto não pode ser anterior '
                    f'ao início do agendamento ({data_fmt}).'
                )
            
            if data_saida and data_fim and data_saida > data_fim:
                data_fmt = data_fim.strftime("%d/%m/%Y %H:%M")
                raise ValidationError(
                    f'A data de saída do trajeto não pode ser posterior '
                    f'ao fim do agendamento ({data_fmt}).'
                )
            
            if data_chegada and data_inicio and data_chegada < data_inicio:
                data_fmt = data_inicio.strftime("%d/%m/%Y %H:%M")
                raise ValidationError(
                    f'A data de chegada do trajeto não pode ser anterior '
                    f'ao início do agendamento ({data_fmt}).'
                )
            
            if data_chegada and data_fim and data_chegada > data_fim:
                data_fmt = data_fim.strftime("%d/%m/%Y %H:%M")
                raise ValidationError(
                    f'A data de chegada do trajeto não pode ser posterior '
                    f'ao fim do agendamento ({data_fmt}).'
                )

        # Atualiza o agendamento
        with transaction.atomic():
            agendamento = form.save()
            formset.save()

        return agendamento

    @staticmethod
    def pode_editar(agendamento, usuario):
        """
        Verifica se o usuário pode editar o agendamento.

        Args:
            agendamento: Agendamento a ser editado
            usuario: Usuário tentando editar

        Returns:
            tuple: (bool, str) - (pode_editar, mensagem_erro)
        """
        if (not usuario.is_administrador() and
                agendamento.professor != usuario):
            return (
                False,
                'Você não tem permissão para editar este agendamento.'
            )

        if agendamento.status != 'pendente':
            return (
                False,
                'Apenas agendamentos pendentes podem ser editados.'
            )

        return True, ''

    @staticmethod
    def pode_deletar(agendamento, usuario):
        """
        Verifica se o usuário pode deletar o agendamento.

        Args:
            agendamento: Agendamento a ser deletado
            usuario: Usuário tentando deletar

        Returns:
            tuple: (bool, str) - (pode_deletar, mensagem_erro)
        """
        if (not usuario.is_administrador() and
                agendamento.professor != usuario):
            return (
                False,
                'Você não tem permissão para deletar este agendamento.'
            )

        if agendamento.status == 'aprovado':
            return (
                False,
                'Agendamentos aprovados não podem ser deletados.'
            )

        return True, ''

    @staticmethod
    def aprovar_agendamento(agendamento):
        """
        Aprova um agendamento.

        Args:
            agendamento: Agendamento a ser aprovado

        Raises:
            ValidationError: Se ultrapassar limite de KM
        """
        agendamento.aprovar()

    @staticmethod
    def reprovar_agendamento(agendamento, motivo):
        """
        Reprova um agendamento.

        Args:
            agendamento: Agendamento a ser reprovado
            motivo: Motivo da reprovação
        """
        agendamento.reprovar(motivo)


class RelatorioService:
    """
    Serviço para geração de relatórios e estatísticas.
    """

    @staticmethod
    def obter_estatisticas_status(agendamentos):
        """
        Calcula estatísticas por status.

        Args:
            agendamentos: QuerySet de agendamentos

        Returns:
            dict: Estatísticas por status
        """
        return agendamentos.values('status').annotate(
            total=Count('id')
        ).order_by('status')

    @staticmethod
    def obter_estatisticas_cursos(agendamentos):
        """
        Calcula estatísticas de KM por curso.

        Args:
            agendamentos: QuerySet de agendamentos aprovados

        Returns:
            dict: Dicionário com estatísticas por curso
        """
        cursos_km = {}
        for agendamento in agendamentos:
            curso_nome = agendamento.curso.nome
            km_agendamento = agendamento.get_total_km()

            if curso_nome not in cursos_km:
                cursos_km[curso_nome] = {
                    'km_total': 0,
                    'agendamentos': 0,
                    'limite_mensal': agendamento.curso.limite_km_mensal
                }

            cursos_km[curso_nome]['km_total'] += km_agendamento
            cursos_km[curso_nome]['agendamentos'] += 1

        # Calcular percentual de uso do limite para cada curso
        for curso_nome, dados in cursos_km.items():
            if dados['limite_mensal'] > 0:
                dados['percentual_uso'] = (
                    dados['km_total'] / dados['limite_mensal']
                ) * 100
            else:
                dados['percentual_uso'] = 0
            dados['km_disponivel'] = (
                dados['limite_mensal'] - dados['km_total']
            )

        return cursos_km

    @staticmethod
    def obter_estatisticas_veiculos(agendamentos, page_size=5):
        """
        Calcula estatísticas por veículo.

        Args:
            agendamentos: QuerySet de agendamentos
            page_size: Número de itens por página (não paginado aqui)

        Returns:
            QuerySet: Estatísticas por veículo
        """
        return agendamentos.values(
            'veiculo__placa',
            'veiculo__marca',
            'veiculo__modelo'
        ).annotate(
            total_agendamentos=Count('id')
        ).order_by('-total_agendamentos')

    @staticmethod
    def obter_estatisticas_professores(agendamentos):
        """
        Calcula estatísticas por professor.

        Args:
            agendamentos: QuerySet de agendamentos

        Returns:
            list: Lista com estatísticas por professor
        """
        professores_stats_list = []
        professores = Usuario.objects.filter(
            tipo_usuario='professor'
        ).order_by('first_name', 'last_name')

        for professor in professores:
            professor_agendamentos = agendamentos.filter(
                professor=professor
            )

            # Calcular total de KM
            total_km = sum(
                ag.get_total_km() for ag in professor_agendamentos
            )

            stats = {
                'professor': professor,
                'professor__first_name': professor.first_name,
                'professor__last_name': professor.last_name,
                'total_km': total_km,
                'total_agendamentos': professor_agendamentos.count(),
                'pendentes': professor_agendamentos.filter(
                    status='pendente'
                ).count(),
                'aprovados': professor_agendamentos.filter(
                    status='aprovado'
                ).count(),
                'reprovados': professor_agendamentos.filter(
                    status='reprovado'
                ).count(),
            }

            # Só incluir professores com agendamentos
            if stats['total_agendamentos'] > 0:
                professores_stats_list.append(stats)

        # Ordenar por total de KM (maior para menor)
        professores_stats_list.sort(
            key=lambda x: x['total_km'],
            reverse=True
        )

        return professores_stats_list

    @staticmethod
    def aplicar_filtros(queryset, filtros):
        """
        Aplica filtros a um queryset de agendamentos.

        Args:
            queryset: QuerySet base
            filtros: Dict com filtros a aplicar

        Returns:
            QuerySet: QuerySet filtrado
        """
        if filtros.get('status'):
            queryset = queryset.filter(status=filtros['status'])

        if filtros.get('curso_id'):
            queryset = queryset.filter(curso_id=filtros['curso_id'])

        if filtros.get('professor_search'):
            search = filtros['professor_search']
            queryset = queryset.filter(
                Q(professor__first_name__icontains=search) |
                Q(professor__last_name__icontains=search) |
                Q(professor__email__icontains=search) |
                Q(professor__username__icontains=search)
            )

        if filtros.get('data_inicio'):
            queryset = queryset.filter(
                data_inicio__gte=filtros['data_inicio']
            )

        if filtros.get('data_fim'):
            queryset = queryset.filter(data_fim__lte=filtros['data_fim'])

        return queryset
