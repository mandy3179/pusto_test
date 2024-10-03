from typing import Generator

from django.db.models.query import QuerySet
from django.http import StreamingHttpResponse, HttpRequest

from second_task.models import PlayerLevel


def generate_csv_rows(queryset: QuerySet) -> Generator[list[str], None, None]:
    """
    Генератор для создания строк CSV из заданного queryset.

    Args:
        queryset (QuerySet): Запрос для получения данных о игроках и уровнях.

    Yields:
        list: Список, представляющий строку CSV, содержащий ID игрока, название уровня и статус завершения.
    """
    yield ['Player ID', 'Level Title', 'Is Completed', 'Prize']
    for row in queryset:
        yield row

def streaming_csv(request: HttpRequest) -> StreamingHttpResponse:
    """
    Обработка запроса для выгрузки данных о игроках и уровнях в CSV файл.

    Args:
        request (HttpRequest): Запрос от клиента.

    Returns:
        StreamingHttpResponse: Ответ с содержимым в формате CSV.
    """
    queryset = PlayerLevel.objects.select_related(
        'player', 'level'
    ).prefetch_related(
        'level__levelprize_set'
    ).values_list(
        'player__player_id',
        'level__title',
        'is_completed',
        'level__levelprize__prize__title'
    )

    response = StreamingHttpResponse(
        (','.join(map(str, row)) + '\n' for row in generate_csv_rows(queryset)),
        content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="users.csv"'
    return response
