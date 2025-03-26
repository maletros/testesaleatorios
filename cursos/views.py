from django.shortcuts import render, get_object_or_404, redirect
from .models import Curso, Trilha
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CursoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

def lista_cursos(request):
    # Obter parâmetros de filtro
    search = request.GET.get('search', '')
    categoria = request.GET.get('categoria', '')
    nivel = request.GET.get('nivel', '')
    ordenar = request.GET.get('ordenar', 'recentes')
    
    # Iniciar queryset
    cursos = Curso.objects.all()
    
    # Aplicar filtros de busca
    if search:
        cursos = cursos.filter(
            Q(titulo__icontains=search) | 
            Q(descricao__icontains=search)
        )
    
    # Filtrar por nível
    if nivel:
        cursos = cursos.filter(nivel=nivel)
    
    # Ordenação
    if ordenar == 'recentes':
        cursos = cursos.order_by('-criado_em')
    elif ordenar == 'populares':
        # Aqui seria ideal ter um campo de popularidade, mas por simplicidade usamos id
        cursos = cursos.order_by('-id')
    elif ordenar == 'horas_asc':
        # Suponha que temos um método que calcula horas totais
        cursos = cursos.order_by('modulos__aulas__duracao_minutos')
    elif ordenar == 'horas_desc':
        cursos = cursos.order_by('-modulos__aulas__duracao_minutos')
    
    # Paginação
    paginator = Paginator(cursos, 9)  # 9 cursos por página
    page = request.GET.get('page')
    try:
        cursos_paginados = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um inteiro, exibe a primeira página
        cursos_paginados = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do intervalo, exibe a última página
        cursos_paginados = paginator.page(paginator.num_pages)
    
    # Preparar níveis para o filtro dropdown
    niveis = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]
    
    # Aqui seriam as categorias reais do banco de dados
    categorias = [
        ('programacao', 'Programação'),
        ('data-science', 'Ciência de Dados'),
        ('ia', 'Inteligência Artificial'),
        ('automacao', 'Automação'),
        ('web', 'Desenvolvimento Web'),
    ]
    
    context = {
        'cursos': cursos_paginados,
        'niveis': niveis,
        'categorias': categorias,
        'search': search,
        'nivel_selecionado': nivel,
        'categoria_selecionada': categoria,
        'ordenar': ordenar,
    }
    
    return render(request, 'cursos/lista.html', context)

def detalhe_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Add context variables needed by the template
    inscrito = False
    progresso = 0
    
    # Here you would check if the user is enrolled and calculate progress
    # For now we just set defaults
    
    context = {
        'curso': curso,
        'inscrito': inscrito,
        'progresso': progresso
    }
    
    return render(request, 'cursos/detalhe.html', context)

def trilha_cursos(request, trilha_slug):
    # Buscar a trilha pelo slug
    trilha = get_object_or_404(Trilha, slug=trilha_slug)
    
    # Obter os cursos associados à trilha
    cursos = trilha.cursos.all()
    
    return render(request, 'cursos/trilha.html', {
        'trilha_nome': trilha.nome,
        'trilha_slug': trilha_slug,
        'cursos': cursos
    })

def lista_trilhas(request):
    # Obter parâmetros de filtro
    search = request.GET.get('search', '')
    area = request.GET.get('area', '')
    
    # Iniciar queryset
    trilhas = Trilha.objects.all()
    
    # Aplicar filtros
    if search:
        trilhas = trilhas.filter(
            Q(nome__icontains=search) | 
            Q(descricao__icontains=search)
        )
    
    if area:
        trilhas = trilhas.filter(area=area)
    
    return render(request, 'cursos/lista_trilhas.html', {
        'trilhas': trilhas,
        'search': search,
        'area_selecionada': area
    })

def adicionar_curso(request):
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save()
            messages.success(request, 'Curso adicionado com sucesso!')
            return redirect('cursos:detalhe', curso_id=curso.id)
    else:
        form = CursoForm()
    
    return render(request, 'cursos/adicionar_curso.html', {'form': form})

@login_required
def inscrever_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Normally, you would handle enrollment logic here
    # For now, just simulate success and redirect back
    messages.success(request, f'Você foi inscrito com sucesso no curso {curso.titulo}!')
    return redirect('cursos:detalhe', curso_id=curso.id)
