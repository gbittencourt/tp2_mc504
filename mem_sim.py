import collections
import math

class MemorySimulator:
    def __init__(self, page_size, num_tlb_entries, num_frames, rep_policy, va_bits):
        self.page_size = page_size
        self.num_tlb_entries = num_tlb_entries
        self.num_frames = num_frames    
        self.rep_policy = rep_policy
        self.va_bits = va_bits

        if rep_policy not in ['LRU', 'SecondChance']:
            raise ValueError("Política de substituição inválida. Use 'LRU' ou 'SecondChance'.")

        self.tlb = [None] * num_tlb_entries  
        self.page_table = {} 
        self.frames = [None] * num_frames
        self.rep_func: function = self._lru if rep_policy == 'LRU' else self._second_chance

        # contadores de estatísticas
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0

        self._lru_time_table: list = [math.inf] * num_frames
        self._lru_counting = 0

    def _lru_update(self, frame_number:int) -> None:
        self._lru_counting += 1
        self._lru_time_table[frame_number] = self._lru_counting

    def _lru(self) -> int:
        """
        Encontra o frame_position a ser substituido. Aplicando a política de substituição
        Least-Recently-Updated (LRU).
        """
        max = 0
        for i, time in  enumerate(self._lru_time_table):
            if time < self._lru_time_table[max]:
                max = i

        return max

    def _second_chance(self) -> int:
        pass

    def update_tlb(self, page_number, frame_buffer):
        """
        Atualiza uma posição da tlb. (Direct-Mapping)
        """
        tlb_position = page_number % self.num_tlb_entries
        self.tlb[tlb_position] = (page_number, frame_buffer)

    def alocate_frame(self, page_number: int) -> int:
        """
        Acha uma posição vazia para alocar a página. Caso não tenha,
        aplica uma política de substituição.

        Retorna: retorna o frame_number onde foi alocado.
        """
        for i, frame in enumerate(self.frames):
            if frame is None:
                self.frames[i] = page_number
                return i

        #apply replacement_policy
        replace_pos = self.rep_func()
        old_page = self.frames[replace_pos]

        #revome página vítima
        if old_page in self.page_table:
            del self.page_table[old_page]

        self.frames[replace_pos] = page_number
        return replace_pos
        

    def access_memory(self, virtual_address):
        """
        Simula o acesso a um endereço virtual.
        Deve atualizar os contadores e aplicar a política de substituição se necessário.
        """
        offset_bits = int(math.log2(self.page_size))
        page_number = virtual_address >> offset_bits

        #checa na tlb 
        tlb_position = page_number % self.num_tlb_entries

        if self.tlb[tlb_position] is not None and self.tlb[tlb_position][0] == page_number:
            #tlb_hit
            self.tlb_hits += 1
            #atualizando o contador para lru
            self._lru_update(self.tlb[tlb_position][1])

        else: #tlb miss
            self.tlb_misses += 1

            #verificar page_table
            if self.page_table.get(page_number) is None: #page_fault
                self.page_faults += 1
                #aloco na memória física.
                new_frame_pos = self.alocate_frame(page_number)
                self.page_table[page_number] = new_frame_pos
                
            else:
                new_frame_pos = self.page_table[page_number]

            #atulizando contador lru
            self._lru_update(new_frame_pos)
            self.update_tlb(page_number, new_frame_pos)

        
    def print_statistics(self):
        print("=" * 60)
        print("SIMULADOR DE MEMÓRIA - Estatísticas de Acesso")
        print("=" * 60)
        print(f"Política de Substituição:   {self.rep_policy}")
        print(f"Tamanho da Página:          {self.page_size} bytes")
        print(f"Entradas na TLB:            {self.num_tlb_entries}")
        print(f"Número de Frames:           {self.num_frames}")
        print("-" * 60)
        print(f"TLB Hits:                   {self.tlb_hits:,}")
        print(f"TLB Misses:                 {self.tlb_misses:,}")
        print(f"Page Faults:                {self.page_faults:,}")
        print("=" * 60)
