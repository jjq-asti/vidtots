#!/usr/bin/env python
import os
from dvbobjects.PSI.PAT import *
from dvbobjects.PSI.NIT import *
from dvbobjects.PSI.SDT import *
from dvbobjects.PSI.PMT import *
from dvbobjects.SBTVD.Descriptors import *


tvd_ts_id = 0x073b                  # ID de red.
tvd_orig_network_id = 0x073b        # ID de red original.
ts_freq = 533                       # Frecuencia de transmisión
ts_remote_control_key = 0x05        # Tecla de control remoto.
tvd_service_id_sd = 0xe760          # ID de servicio de TV Digital.
tvd_pmt_pid_sd = 1031               # PID de la PMT del servicio.

nit = network_information_section(
    network_id = tvd_orig_network_id,
    network_descriptor_loop = [
        network_descriptor(network_name = "LIFIATV",),
        system_management_descriptor(
            broadcasting_flag = 0,
            broadcasting_identifier = 3,
            additional_broadcasting_identification = 0x01,
            additional_identification_bytes = [],
        )
    ],
    transport_stream_loop = [
        transport_stream_loop_item(
            transport_stream_id = tvd_ts_id,
            original_network_id = tvd_orig_network_id,
            transport_descriptor_loop = [
                service_list_descriptor(
                    dvb_service_descriptor_loop = [
                        service_descriptor_loop_item (
                            service_ID = tvd_service_id_sd,
                            service_type = 1,
                        ),
                    ],
                ),
                terrestrial_delivery_system_descriptor(
                    area_code = 1341,
                    guard_interval = 0x01,
                    transmission_mode = 0x02,
                    frequencies = [
                        tds_frequency_item( freq=ts_freq )
                    ],
                ),
                partial_reception_descriptor (
                    service_ids = []
                ),
                transport_stream_information_descriptor (
                    remote_control_key_id = ts_remote_control_key,
                    ts_name = "LIFIATV",
                    transmission_type_loop = [
                        transmission_type_loop_item(
                            transmission_type_info = 0x0F,
                            service_id_loop = [
                                service_id_loop_item(
                                    service_id=tvd_service_id_sd
                                ),
                            ]
                        ),
                        transmission_type_loop_item(
                            transmission_type_info = 0xAF,
                            service_id_loop = [],
                        ),
                    ],
                )
            ],
        ),
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)

sdt = service_description_section(
    transport_stream_id = tvd_ts_id,
    original_network_id = tvd_orig_network_id,
    service_loop = [
        service_loop_item(
            service_ID = tvd_service_id_sd,
            EIT_schedule_flag = 0,
            EIT_present_following_flag = 0,
            running_status = 4,
            free_CA_mode = 0,
            service_descriptor_loop = [
                service_descriptor(
                    service_type = 1,
                    service_provider_name = "",
                    service_name = "LFASD",
                ),
            ],
        ),
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)


pat = program_association_section(
    transport_stream_id = tvd_ts_id,
    program_loop = [
        program_loop_item(
            # Programa especial para la tabla NIT
            program_number = 0,
            PID = 16,
        ),
        program_loop_item(
            program_number = tvd_service_id_sd,
            PID = tvd_pmt_pid_sd,
        ),
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)

pmt_sd = program_map_section(
    program_number = tvd_service_id_sd,
    PCR_PID = 2064,
    program_info_descriptor_loop = [],
    stream_loop = [
        stream_loop_item(
            stream_type = 2, # mpeg2 video stream type
            elementary_PID = 2064,
            element_info_descriptor_loop = [
            ]
        ),
        stream_loop_item(
        stream_type = 3, # mpeg2 audio stream type
        elementary_PID = 2068,
        element_info_descriptor_loop = []
        ),
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)


out = open("./nit.sec", "wb")
out.write(nit.pack())
out.close()
os.system("sec2ts 16 < ./nit.sec > ./nit.ts")
out = open("./pat.sec", "wb")
out.write(pat.pack())
out.close()
os.system("sec2ts 0 < ./pat.sec > ./pat.ts")
out = open("./sdt.sec", "wb")
out.write(sdt.pack())
out.close()
os.system("sec2ts 17 < ./sdt.sec > ./sdt.ts")
out = open("./pmt_sd.sec", "wb")
out.write(pmt_sd.pack())
out.close()
os.system("sec2ts " + str(tvd_pmt_pid_sd) +
" < ./pmt_sd.sec > ./pmt_sd.ts")



ait = application_information_section (
    application_type = 0x0009, # GINGA-NCL common_descriptor_loop = [],
    application_loop = [
        application_loop_item (
            organization_id = 0x0000000A,
            application_id = 0x64,
            application_control_code = 0x01, # AUTOSTART
            application_descriptors_loop = [
                transport_protocol_descriptor (
                    protocol_id = 0x0001,
                    transport_protocol_label = 0,
                    remote_connection = 0,
                    component_tag = 0x0C, # association_tag
                ),
                application_descriptor (
                    application_profile = 0x0001,
                    version_major = 1,
                    version_minor = 0,
                    version_micro = 0,
                    service_bound_flag = 1,
                    visibility = 3,
                    application_priority = 1,
                    transport_protocol_labels = [0],
                ),
                application_name_descriptor (
                    application_name = "APP_GINGA"
                ),
                ginga_ncl_application_descriptor (
                    parameters = []
                ),
                ginga_ncl_application_location_descriptor (
                    base_directory = "/",
                    class_path_extension = "",
                    initial_class = "main.ncl", # name of the NCL file
                    # to be executed.
                ),
            ]
        ),
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
),


pmt_sd = program_map_section(
    program_number = tvd_service_id_sd,
    PCR_PID = 2064,
    program_info_descriptor_loop = [],
    stream_loop = [
        stream_loop_item(
            stream_type = 2, # mpeg2 video stream type
            elementary_PID = 2064,
            element_info_descriptor_loop = [
            ]
        ),
        stream_loop_item(
            stream_type = 3, # mpeg2 audio stream type
            elementary_PID = 2068,
            element_info_descriptor_loop = []
        ),
        stream_loop_item(
            stream_type = 5, # AIT stream type
            elementary_PID = 2001,
            element_info_descriptor_loop = [
            data_component_descriptor (
                data_component_id = 0xA3, # sistema AIT
                additional_data_component_info = ait_identifier_info(
                    application_type = GINGA_NCL_application_type,
                    ait_version
                    = 0
                ).bytes(),
            ),
                application_signalling_descriptor(
                    application_type = 9, # 9 GINGA-NCL
                    AIT_version = 1, # current ait version
                ),
            ]
        ), stream_loop_item(
            stream_type = 0x0B, # DSMCC stream type
            elementary_PID = 2004,
            element_info_descriptor_loop = [
                association_tag_descriptor(
                    association_tag = 0x0C,
                    use = 0,
                    selector_lenght = 0,
                    transaction_id = 0x80000000,
                    timeout = 0xFFFFFFFF,
                    private_data = "",
                ),
                stream_identifier_descriptor(
                    component_tag = 0x0C,
                ),
                carousel_identifier_descriptor(
                    carousel_ID = 2,
                    format_ID = 0,
                    private_data = "",
                ),
                data_component_descriptor (
                    data_component_id = 0xA0, # sistema GINGA
                    additional_data_component_info = additional_ginga_j_info(
                    transmission_format = 0x2,
                      cument_resolution = 0x5,
                    organization_id = 0x0000000A, 
                    application_id = 0x0064,
                    carousel_id = 2,
                    ).bytes(),
                ),
            ]
        )
    ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)

out = open("./ait.sec", "wb")
out.write(ait.pack())
out.close()
os.system('sec2ts ' + str(2001) + ' < ./ait.sec > ./ait.ts')


group = Group (
    PATH = "DII.sec",
    transactionId = 0x80000002,
    downloadId = 0x00000001,
    blockSize = 4066,
    version = 1,
)

group.set (
compatibilityDescriptor = comp_desc.pack (),
modules = [
    Module (
        INPUT = "firmware_nuevo.dat",
        moduleId = 0x0001,
        moduleVersion = 0x00,
        descriptors = [
            type_descriptor (mime_type = "application / x-download"),
            name_descriptor (name = "firmware.20100908.dat"),
        ],
    ),
],
)

group.generate ("carousel")



sdtt = software_download_trigger_table (
transport_stream_id = tvd_ts_id,
original_network_id = tvd_orig_network_id,
service_id
= tvd_service_id_eng,
maker_id = maker_id,
model_id = model_id,
contents
= [
    sdtt_content_loop_item (
        group = group_id,
        target_version = targetversion_id,
        new_version = newversion_id,
        download_level = download_level,
        version_indicator = version_indicator,
        schedule_timeshift_information = 0x00,
        schedule_loop_items = [
            # Hoy, desde la 01:00:00 hasta las 23:59:59
            sdtt_schedule_loop_item (
                start_year = timenow.year - 1900, # since 1900
                start_month = timenow.month,
                start_day = timenow.day,
                start_hour = 0x01,
                start_minute= 0x00,
                start_second= 0x00,
                duration_hours
                = 0x23,
                duration_minutes = 0x59,
                duration_seconds = 0x59,
            ),
        ],
        descriptors = [
            download_content_descriptor (
                reboot = 0,
                add_on = 1,
                component_size = 0x00,
                download_id = 0x00000001,
                time_out_value_DII = 36600000,
                leak_rate = 0x00,
                component_tag = dsmcc_association_tag,
                compatibility_descriptor_bytes = comp_desc.pack(),
                modules_info_bytes = "",
                privateData = "",
                text_ISO639_lang = "",
                text_data = "",
            )
        ],
    )
   ],
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
)

out = open("sdtt.sec", "wb")
out.write(sdtt.pack())
out.close()
# PID 35 (0x23): Low protection layer
os.system('sec2ts 35 < sdtt.sec > sdtt.ts')
out = open("pmt_eng.sec", "wb")
out.write(pmt_eng.pack())
out.close()
os.system('sec2ts ' + str(tvd_pmt_pid_eng) + ' < pmt_eng.sec > pmt_eng.ts')