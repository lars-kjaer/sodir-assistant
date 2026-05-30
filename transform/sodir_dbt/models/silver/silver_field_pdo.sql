with source as (
    select * from {{ source('bronze', 'bronze_field_pdo') }}
),

renamed as (
    select
        fldName           as    field_name,
        fldPudApproved    as    field_plan_development_operation_approved,
        fldPudDescription as    field_plan_development_operation_description,
        fldPudType        as    field_plan_development_operation_type,
        fldNpdidField     as    npdid_field
    from source
)

select * from renamed