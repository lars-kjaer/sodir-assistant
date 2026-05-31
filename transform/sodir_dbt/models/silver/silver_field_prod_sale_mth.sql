with source as (
    select * from {{ source('bronze', 'bronze_field_prod_sale_mth') }}
),

renamed as (
    select
        prfInformationCarrier               AS  field_name,
        prfYear                             AS  year,
        prfMonth                            AS  month,
        prfPrdOilNetMillSm3                 AS  net_oil_million_sm3,
        prfPrdGasNetBillSm3                 AS  net_gas_billion_sm3,
        prfPrdNGLNetMillSm3                 AS  net_ngl_million_sm3,
        prfPrdCondensateNetMillSm3          AS  net_condensate_million_sm3,
        prfPrdOeNetMillSm3                  AS  net_oil_equivalent_million_sm3,
        prfPrdProducedWaterInFieldMillSm3   AS  produced_water_in_field_million_sm3,
        prfNpdidInformationCarrier          AS  npdid_field
    from source
)

select * from renamed