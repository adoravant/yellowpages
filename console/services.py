class MatrixService:
    @staticmethod
    def get_scenario_for_lead(lead_progress):
        """
        Determina qué MatrixScenario corresponde según el stage actual 
        y la cantidad de interacciones acumuladas.
        """
        from sales.models import Event
        
        # 1. Contamos cuántas replies hubo en este stage para este lead
        # Esto define la 'iteración' (fricción)
        iteration = Event.objects.filter(
            lead=lead_progress.lead,
            event_type__slug__icontains=f"reply_{lead_progress.current_stage.lower()}"
        ).count()

        # 2. Buscamos el escenario configurado (o fallback a iteración 0)
        scenario = MatrixScenario.objects.filter(
            stage=lead_progress.current_stage,
            iteration=iteration
        ).first()

        if not scenario:
            # Fallback al escenario inicial de la etapa si no hay uno específico para la iteración
            scenario = MatrixScenario.objects.filter(
                stage=lead_progress.current_stage,
                iteration=0
            ).first()
            
        return scenario