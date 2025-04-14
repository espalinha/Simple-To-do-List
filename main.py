import tkinter as tk
from tkinter import Menu
import csv

class App(tk.Tk):
    def __init__(self, divisoes=7, width = 1200, height=700):
        super().__init__()

        self.title("Container com Frames")
        self.each_frame_size = []
        self.divisoes = divisoes
        self.width = width
        self.height = height
        self.week = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sabado"]
        self.subjects = []
        self.marked = []
        self.priority_colors = {
            0: "white",   # Não marcado
            1: "#90EE90",  # Verde claro (Concluído)
            2: "#FFD700",  # Amarelo (Importante)
            3: "#FF6347"   # Vermelho (Urgente)
        }
        self.botoes = [[] for _ in range(self.divisoes)]

        self.each_frame_size.append(((width-150)/divisoes))
        self.each_frame_size.append(height - 40)
        self.geometry(f"{self.width}x{self.height}")
        self._read_csv()
        self._read_marked()
        self._adjust_data_consistency()
        self._cria_menu()
        self._criar_interface()

    def _cria_menu(self):
        mb = tk.Menubutton(self, text="Configurações", relief=tk.RAISED)
        mb.pack(anchor="nw", padx=10, pady=10)

        menu = Menu(mb, tearoff=0)
        mb["menu"] = menu

        menu.add_command(label="Adicionar Tarefa", command=self._add)
        menu.add_command(label="Editar Tarefas", command=self._abrir_janela_edicao)  # ← LINHA ADICIONADA
        menu.add_separator()
        menu.add_command(label="Limpar Marcadores", command=self._clean)
        menu.add_command(label="Salvar Agora", command=self._salvar_todos)
        menu.add_command(label="Sair", command=self._destroy)

    def _criar_menu_prioridades(self, event, day_index, task_index):
        menu = Menu(self, tearoff=0)
        prioridades = {
            "Sem prioridade": 0,
            "Concluído (Verde)": 1,
            "Importante (Amarelo)": 2,
            "Urgente (Vermelho)": 3
        }

        for texto, valor in prioridades.items():
            menu.add_command(
                label=texto,
                command=lambda v=valor: self._atualizar_prioridade(
                    day_index, task_index, v
                )
            )
        menu.tk_popup(event.x_root, event.y_root)

    def _atualizar_prioridade(self, day_index, task_index, prioridade):
        self.marked[day_index][task_index] = prioridade
        self.botoes[day_index][task_index].config(
            bg=self.priority_colors[prioridade]
        )
        self._salvar_todos()
    def _adjust_data_consistency(self):
        # Garantir que subjects tenha exatamente 7 dias
        while len(self.subjects) < self.divisoes:
            idx = len(self.subjects)
            self.subjects.append([self.week[idx]])
        self.subjects = self.subjects[:self.divisoes]

        # Garantir que marked tenha exatamente 7 dias
        while len(self.marked) < self.divisoes:
            self.marked.append([])
        self.marked = self.marked[:self.divisoes]

        # Ajustar cada marked[i] para ter o mesmo número de tarefas que subjects[i]
        for i in range(self.divisoes):
            num_tarefas = len(self.subjects[i]) - 1
            if len(self.marked[i]) > num_tarefas:
                self.marked[i] = self.marked[i][:num_tarefas]
            elif len(self.marked[i]) < num_tarefas:
                self.marked[i] += [0] * (num_tarefas - len(self.marked[i]))

    def _abrir_janela_edicao(self):
            janela = tk.Toplevel(self)
            janela.title("Editar Tarefas")
            janela.geometry("400x300")
            janela.grab_set()
            janela.focus_force()

            # --- Variáveis de controle ---
            dia_var = tk.StringVar(janela, value=self.week[0])
            tarefa_var = tk.StringVar(janela)

            # --- Widgets ---
            tk.Label(janela, text="Dia da semana:").pack(pady=5)
            om_dia = tk.OptionMenu(janela, dia_var, *self.week)
            om_dia.pack()

            tk.Label(janela, text="Tarefa:").pack(pady=5)
            om_tarefa = tk.OptionMenu(janela, tarefa_var, "")
            om_tarefa.pack()

            # --- Frame para botões ---
            frame_botoes = tk.Frame(janela)
            frame_botoes.pack(pady=15)

            # Criando os botões primeiro
            btn_editar = tk.Button(frame_botoes, text="Editar", state="disabled")
            btn_excluir = tk.Button(frame_botoes, text="Excluir", state="disabled")
            btn_subir = tk.Button(frame_botoes, text="▲ Subir", state="disabled")
            btn_descer = tk.Button(frame_botoes, text="▼ Descer", state="disabled")

            btn_editar.pack(side="left", padx=5)
            btn_excluir.pack(side="left", padx=5)
            btn_subir.pack(side="left", padx=5)
            btn_descer.pack(side="left", padx=5)

            # --- Função de atualização ---
            def atualiza_tarefas(*_):
                dia_idx = self.week.index(dia_var.get())
                tarefas = self.subjects[dia_idx][1:]
                menu = om_tarefa["menu"]
                menu.delete(0, "end")
                
                if not tarefas:
                    tarefa_var.set("(Nenhuma tarefa)")
                    for btn in [btn_editar, btn_excluir, btn_subir, btn_descer]:
                        btn.config(state="disabled")
                else:
                    for t in tarefas:
                        menu.add_command(label=t, command=lambda v=t: tarefa_var.set(v))
                    tarefa_var.set(tarefas[0])
                    for btn in [btn_editar, btn_excluir, btn_subir, btn_descer]:
                        btn.config(state="normal")

            # Configura comandos dos botões após criá-los
            btn_editar.config(command=lambda: self._editar_tarefa(
                self.botoes[self.week.index(dia_var.get())][self.subjects[self.week.index(dia_var.get())].index(tarefa_var.get()) - 1],
                self.week.index(dia_var.get()),
                self.subjects[self.week.index(dia_var.get())].index(tarefa_var.get()) - 1
            ))

            btn_excluir.config(command=lambda: self._excluir_tarefa(
                self.week.index(dia_var.get()),
                self.subjects[self.week.index(dia_var.get())].index(tarefa_var.get()) - 1
            ))

            btn_subir.config(command=lambda: self._mover_tarefa(
                self.week.index(dia_var.get()),
                self.subjects[self.week.index(dia_var.get())].index(tarefa_var.get()) - 1,
                "cima"
            ))

            btn_descer.config(command=lambda: self._mover_tarefa(
                self.week.index(dia_var.get()),
                self.subjects[self.week.index(dia_var.get())].index(tarefa_var.get()) - 1,
                "baixo"
            ))

            # --- Configura rastreamento ---
            dia_var.trace_add("write", atualiza_tarefas)
            tarefa_var.trace_add("write", lambda *_: None)  # Placeholder para futuras atualizações
            atualiza_tarefas()  # Carrega inicialmente

        # Habilita/desabilita botões conforme seleção
    def _editar_tarefa(self, botao, dia_idx, task_idx):
            nova_janela = tk.Toplevel(self)
            nova_janela.title("Editar Nome da Tarefa")
            nova_janela.geometry("300x150")
            
            tk.Label(nova_janela, text="Novo nome:").pack(pady=10)
            entrada = tk.Entry(nova_janela, width=25)
            entrada.insert(0, self.subjects[dia_idx][task_idx + 1])
            entrada.pack()
            
            def confirmar():
                novo_nome = entrada.get().strip()
                if novo_nome:
                    self.subjects[dia_idx][task_idx + 1] = novo_nome
                    botao.config(text=novo_nome)
                    self._salvar_todos()
                    nova_janela.destroy()
            
            tk.Button(nova_janela, text="Salvar", command=confirmar).pack(pady=10)

    def _excluir_tarefa(self, dia_idx, task_idx):
            self.subjects[dia_idx].pop(task_idx + 1)
            self.marked[dia_idx].pop(task_idx)
            self._salvar_todos()
            self._recarregar_interface()

    def _mover_tarefa(self, dia_idx, task_idx, direcao):
            if direcao == "cima" and task_idx > 0:
                # Move para cima
                self.subjects[dia_idx][task_idx + 1], self.subjects[dia_idx][task_idx] = (
                    self.subjects[dia_idx][task_idx],
                    self.subjects[dia_idx][task_idx + 1]
                )
                self.marked[dia_idx][task_idx], self.marked[dia_idx][task_idx - 1] = (
                    self.marked[dia_idx][task_idx - 1],
                    self.marked[dia_idx][task_idx]
                )
            elif direcao == "baixo" and task_idx < len(self.subjects[dia_idx]) - 2:
                # Move para baixo
                self.subjects[dia_idx][task_idx + 1], self.subjects[dia_idx][task_idx + 2] = (
                    self.subjects[dia_idx][task_idx + 2],
                    self.subjects[dia_idx][task_idx + 1]
                )
                self.marked[dia_idx][task_idx], self.marked[dia_idx][task_idx + 1] = (
                    self.marked[dia_idx][task_idx + 1],
                    self.marked[dia_idx][task_idx]
                )
            
            self._salvar_todos()
            self._recarregar_interface()
    def _read_csv(self):
        self.subjects = []
        try:
            with open('schedules.csv', mode='r') as file:
                csvFile = csv.reader(file)
                for lines in csvFile:
                    self.subjects.append([item.strip() for item in lines if item.strip() != ''])
        except FileNotFoundError:
            self.subjects = []
        self._remove_empty()

    def _remove_empty(self):
        self.subjects = [linha for linha in self.subjects if linha]
        # Garantir que cada linha comece com o nome correto do dia
        for i in range(len(self.subjects)):
            if i < len(self.week) and (len(self.subjects[i]) == 0 or self.subjects[i][0] != self.week[i]):
                self.subjects[i] = [self.week[i]] + self.subjects[i][1:]

    def _read_marked(self):
        self.marked = []
        try:
            with open('marked.csv', mode='r') as file:
                csvFile = csv.reader(file)
                for lines in csvFile:
                    if lines and len(lines) > 0:
                        marcacoes = []
                        for item in lines[1:]:
                            if item.strip() == '+':  # Compatibilidade com versão anterior
                                marcacoes.append(1)
                            elif item.strip() == '-':
                                marcacoes.append(0)
                            else:
                                marcacoes.append(int(item.strip()))
                        self.marked.append(marcacoes)
        except (FileNotFoundError, ValueError):
            self.marked = []
            
    def _add(self):
        janela = tk.Toplevel(self)
        janela.geometry("500x300")
        janela.title("Adicionar Tarefa")

        tk.Label(janela, text="Dia da semana:").pack(pady=5)
        dia_var = tk.StringVar(janela)
        dia_var.set(self.week[0])
        tk.OptionMenu(janela, dia_var, *self.week).pack()

        tk.Label(janela, text="Tarefa:").pack(pady=5)
        entrada = tk.Entry(janela)
        entrada.pack()

        def confirmar():
            dia = dia_var.get()
            tarefa = entrada.get().strip()
            if tarefa:
                idx = self.week.index(dia)
                self.subjects[idx].append(tarefa)
                self.marked[idx].append(0)
                self._salvar_todos()
                janela.destroy()
                self._recarregar_interface()

        tk.Button(janela, text="Confirmar", command=confirmar).pack(pady=10)
           
    def _recarregar_interface(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        self._criar_interface()
    def _destroy(self):
        self._salvar_todos()
        self.destroy()
    def _clean(self):
        for i in range(len(self.marked)):
            for j in range(len(self.marked[i])):
                self.marked[i][j-1] = 0
                try:
                    self.botoes[i][j].config(bg="white")
                except IndexError:
                # Caso o botão correspondente não exista (diferença de tamanho entre marked e botoes)
                    pass
                                              
    def _salvar_todos(self):
        self._copy_all()
        print("Arquivos salvos com sucesso!")

    def _copy_all(self):
        # Salvar subjects.csv
        with open("schedules.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            for linha in self.subjects:
                writer.writerow(linha)
        # Salvar marked.csv
        with open("marked.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            for i in range(self.divisoes):
                linha_convertida = [self.week[i]] + ['+' if val == 1 else '-' for val in self.marked[i]]
                writer.writerow(linha_convertida)

    def _criar_interface(self):
        container = tk.Frame(self, padx=2, pady=20)
        container.pack()

        for ii in range(self.divisoes):
            divisao = tk.Frame(
                container,
                width=self.each_frame_size[0],
                height=self.each_frame_size[1],
                bg="white", bd=1, relief="solid", padx=2
            )
            divisao.pack_propagate(False)
            label = tk.Label(divisao, text=self.week[ii])
            label.pack()

            self.botoes[ii] = []  # Resetar a lista de botões

            for k, sub in enumerate(self.subjects[ii]):
                if k != 0:
                    # Usar as cores de prioridade corretas
                    priority = self.marked[ii][k-1]
                    btn = tk.Button(
                        divisao,
                        text=f"{sub}",
                        bg=self.priority_colors[priority],
                        wraplength=150,
                        anchor=tk.W,
                        justify=tk.LEFT
                    )
                    
                    # Vincular eventos
                    btn.bind("<Button-1>", lambda e, i=ii, j=k-1: self._toggle_concluido(i, j))
                    btn.bind("<Button-3>", lambda e, i=ii, j=k-1: self._criar_menu_prioridades(e, i, j))
                    
                    btn.pack(side=tk.TOP, padx=5, pady=10, fill=tk.X)
                    self.botoes[ii].append(btn)

            divisao.pack(side="left", padx=10)

    def _toggle_concluido(self, day_index, task_index):
    # Alternar entre 0 (não concluído) e 1 (concluído)
        current = self.marked[day_index][task_index]
        new_value = 1 if current == 0 else 0
        self.marked[day_index][task_index] = new_value
        self.botoes[day_index][task_index].config(
            bg=self.priority_colors[new_value]
        )
        self._salvar_todos()

if __name__ == "__main__":
    app = App()
    app.mainloop()
