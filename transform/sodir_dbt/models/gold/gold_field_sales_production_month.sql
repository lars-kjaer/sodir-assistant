with source as (
    select * from {{ ref('silver_field_prod_sale_mth') }}
),

derive_uom_variants as (
    select
        field_name,
        year,
        month,
        net_oil_million_sm3,
        net_oil_million_sm3 * 6.2898 AS net_oil_million_bbl,
        net_gas_billion_sm3,
        net_gas_billion_sm3 * 35.3147 AS net_gas_billion_scf,
        net_ngl_million_sm3,
        net_ngl_million_sm3 * 6.2898 AS net_ngl_million_bbl,
        net_condensate_million_sm3,
        net_condensate_million_sm3 * 6.2898 AS net_condensate_million_bbl,
        net_oil_equivalent_million_sm3,
        net_oil_equivalent_million_sm3 * 6.2898 AS net_oil_equivalent_million_bbl,
        produced_water_in_field_million_sm3,
        produced_water_in_field_million_sm3 * 6.2898 AS produced_water_in_field_million_bbl,
        npdid_field
    from source
)

select * from derive_uom_variants