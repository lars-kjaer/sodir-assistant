with source as (
    select * from {{ source('bronze', 'wellbore_all') }}
),

renamed as (
    select
        wlbWellboreName         as wellbore_name,
        wlbNpdidWellbore        as wellbore_id,
        wlbWell                 as well_name,
        wlbWellType             as wellbore_type,
        wlbDrillingOperator     as drilling_operator,
        wlbProductionLicence    as production_licence,
        wlbPurpose              as wellbore_purpose,
        wlbStatus               as wellbore_status,
        wlbContent              as wellbore_content,
        wlbEntryDate            as wellbore_spud_date,
        wlbCompletionDate       as wellbore_completion_date,
        wlbField                as field_name,
        wlbMainArea             as main_area,
        wlbSubSea               as subsea,
        wlbWaterDepth           as water_depth_meter,
        wlbTotalDepth           as total_depth_meter,
        wlbDrillingDays         as drilling_days,
        wlbDrillingFacility     as drilling_facility,
        wlbFormationAtTd        as oldest_penetrated_formation,
        wlbAgeAtTd              as oldest_penetrated_age,
        wlbPluggedDate          as plugged_date,
        wlbPluggedAbandonDate   as plug_and_abandon_date,
        wlbEntryYear            as entry_year,
        wlbCompletionYear       as completion_year
    from source
)

select * from renamed