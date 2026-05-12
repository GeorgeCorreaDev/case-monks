from __future__ import annotations

import functools
from google.cloud import bigquery
from google.api_core import exceptions as gcp_exc

from core import settings, bq_execution_error, bq_validation_error


# lazy singleton .. conecta se preciso
# evita overhead
class _bq_service:
    _client: bigquery.Client | None = None
    _cache: dict = {} # cache simple d memoria

    @property
    def client(self) -> bigquery.Client:
        if self._client is None:
            project = settings.gcp_project_id
            if not project:
                raise bq_validation_error("gcp_project_id nao configurado no .env")
            self._client = bigquery.Client(project=project)
        return self._client

    def _run_query(
        self,
        sql: str,
        params: list[bigquery.ScalarQueryParameter] | None = None,
    ) -> list[dict]:
        # cache key baseada no sql
        cache_key = f"{sql}_{str(params)}"
        
        if settings.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # roda a query
        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = params

        try:
            result = self.client.query(sql, job_config=job_config).result()
            rows = [dict(row) for row in result]
            
            if settings.enable_cache:
                self._cache[cache_key] = rows
                
            return rows
        except gcp_exc.BadRequest as e:
            raise bq_execution_error(f"sql invalido: {e}", {"sql": sql}) from e
        except gcp_exc.Forbidden as e:
            raise bq_execution_error(f"sem permissao bq: {e}", {"sql": sql}) from e
        except Exception as e:
            raise bq_execution_error(f"erro inesperado bq: {e}", {"sql": sql}) from e

    # >>queries de negocio<<

    def revenue_by_channel(self, start_date: str, end_date: str) -> list[dict]:
        # receita por canal no periodo
        sql = """
            SELECT
                u.traffic_source AS canal,
                COUNT(DISTINCT oi.order_id) AS total_pedidos,
                ROUND(SUM(oi.sale_price), 2) AS receita_total,
                COUNT(DISTINCT u.id) AS usuarios_unicos
            FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
            JOIN `bigquery-public-data.thelook_ecommerce.users` u
                ON oi.user_id = u.id
            WHERE oi.created_at BETWEEN @start_date AND @end_date
                AND oi.status NOT IN ('Cancelled', 'Returned')
            GROUP BY u.traffic_source
            ORDER BY receita_total DESC
        """
        params = [
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
        return self._run_query(sql, params)

    def conversion_rate_by_channel(self, start_date: str, end_date: str) -> list[dict]:
        # taxa de conv .. compradores vs total por canal
        sql = """
            WITH buyers AS (
                SELECT DISTINCT oi.user_id
                FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
                WHERE oi.created_at BETWEEN @start_date AND @end_date
                  AND oi.status NOT IN ('Cancelled', 'Returned')
            )
            SELECT
                u.traffic_source AS canal,
                COUNT(DISTINCT u.id) AS total_usuarios,
                COUNT(DISTINCT b.user_id) AS compradores,
                ROUND(
                    SAFE_DIVIDE(COUNT(DISTINCT b.user_id), COUNT(DISTINCT u.id)) * 100, 2
                ) AS taxa_conversao
            FROM `bigquery-public-data.thelook_ecommerce.users` u
            LEFT JOIN buyers b ON u.id = b.user_id
            WHERE u.created_at BETWEEN @start_date AND @end_date
            GROUP BY u.traffic_source
            ORDER BY taxa_conversao DESC
        """
        params = [
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
        return self._run_query(sql, params)

    def ticket_medio_by_channel(self, start_date: str, end_date: str) -> list[dict]:
        # ticket medio ; receita / pedidos
        sql = """
            SELECT
                u.traffic_source AS canal,
                COUNT(DISTINCT oi.order_id) AS total_pedidos,
                ROUND(SUM(oi.sale_price), 2) AS receita_total,
                ROUND(
                    SAFE_DIVIDE(SUM(oi.sale_price), COUNT(DISTINCT oi.order_id)), 2
                ) AS ticket_medio
            FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
            JOIN `bigquery-public-data.thelook_ecommerce.users` u
                ON oi.user_id = u.id
            WHERE oi.created_at BETWEEN @start_date AND @end_date
                AND oi.status NOT IN ('Cancelled', 'Returned')
            GROUP BY u.traffic_source
            ORDER BY ticket_medio DESC
        """
        params = [
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
        return self._run_query(sql, params)

    def top_products_by_channel(
        self, channel: str, start_date: str, end_date: str, limit: int = 10
    ) -> list[dict]:
        # top prod vendidos num canal especifico
        sql = f"""
            SELECT
                p.name AS produto,
                p.category AS categoria,
                COUNT(DISTINCT oi.order_id) AS vendas,
                ROUND(SUM(oi.sale_price), 2) AS receita
            FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
            JOIN `bigquery-public-data.thelook_ecommerce.users` u
                ON oi.user_id = u.id
            JOIN `bigquery-public-data.thelook_ecommerce.products` p
                ON oi.product_id = p.id
            WHERE u.traffic_source = @channel
                AND oi.created_at BETWEEN @start_date AND @end_date
                AND oi.status NOT IN ('Cancelled', 'Returned')
            GROUP BY p.name, p.category
            ORDER BY receita DESC
            LIMIT {limit}
        """
        params = [
            bigquery.ScalarQueryParameter("channel", "STRING", channel),
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
        return self._run_query(sql, params)

    def get_schema_info(self) -> list[dict]:
        # traz info das tabelas e colunas 
        # junior sem preguica estuda o banco 
        sql = """
            SELECT table_name, column_name, data_type
            FROM `bigquery-public-data.thelook_ecommerce.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name IN ('users', 'orders', 'order_items', 'products')
        """
        return self._run_query(sql)


# instancia global .. importa com > from services.bq_service import bq
bq = _bq_service()
