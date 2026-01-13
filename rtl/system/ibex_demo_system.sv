// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

// The Ibex demo system, which instantiates and connects the following blocks:
// - Memory bus.
// - CV32E40PX core (replacing Ibex).
// - RAM memory to contain code and data.
// - Two core2axi bridges for user-defined AXI slaves.
// - UART for serial communication.
// - Timer.
// - Debug module.
// - PWM for LED control.
module ibex_demo_system #(
  parameter int                 PwmWidth       = 12,
  parameter int unsigned        ClockFrequency = 50_000_000,
  parameter int unsigned        BaudRate       = 115_200,
  parameter                     SRAMInitFile   = "",
  parameter int                 AXI4_ADDRESS_WIDTH = 32,
  parameter int                 AXI4_RDATA_WIDTH   = 32,
  parameter int                 AXI4_WDATA_WIDTH   = 32,
  parameter int                 AXI4_ID_WIDTH      = 16,
  parameter int                 AXI4_USER_WIDTH    = 10
) (
  input  logic clk_sys_i,
  input  logic rst_sys_ni,

  output logic [PwmWidth-1:0] pwm_o,
  input  logic                uart_rx_i,
  output logic                uart_tx_o,

  // Core2AXI 0 - AXI Master interface (replaces GPIO)
  output logic [AXI4_ID_WIDTH-1:0]      core2axi0_aw_id_o,
  output logic [AXI4_ADDRESS_WIDTH-1:0] core2axi0_aw_addr_o,
  output logic [ 7:0]                   core2axi0_aw_len_o,
  output logic [ 2:0]                   core2axi0_aw_size_o,
  output logic [ 1:0]                   core2axi0_aw_burst_o,
  output logic                          core2axi0_aw_lock_o,
  output logic [ 3:0]                   core2axi0_aw_cache_o,
  output logic [ 2:0]                   core2axi0_aw_prot_o,
  output logic [ 3:0]                   core2axi0_aw_region_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi0_aw_user_o,
  output logic [ 3:0]                   core2axi0_aw_qos_o,
  output logic                          core2axi0_aw_valid_o,
  input  logic                          core2axi0_aw_ready_i,
  output logic [AXI4_WDATA_WIDTH-1:0]   core2axi0_w_data_o,
  output logic [AXI4_WDATA_WIDTH/8-1:0] core2axi0_w_strb_o,
  output logic                          core2axi0_w_last_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi0_w_user_o,
  output logic                          core2axi0_w_valid_o,
  input  logic                          core2axi0_w_ready_i,
  input  logic [AXI4_ID_WIDTH-1:0]      core2axi0_b_id_i,
  input  logic [ 1:0]                   core2axi0_b_resp_i,
  input  logic                          core2axi0_b_valid_i,
  input  logic [AXI4_USER_WIDTH-1:0]    core2axi0_b_user_i,
  output logic                          core2axi0_b_ready_o,
  output logic [AXI4_ID_WIDTH-1:0]      core2axi0_ar_id_o,
  output logic [AXI4_ADDRESS_WIDTH-1:0] core2axi0_ar_addr_o,
  output logic [ 7:0]                   core2axi0_ar_len_o,
  output logic [ 2:0]                   core2axi0_ar_size_o,
  output logic [ 1:0]                   core2axi0_ar_burst_o,
  output logic                          core2axi0_ar_lock_o,
  output logic [ 3:0]                   core2axi0_ar_cache_o,
  output logic [ 2:0]                   core2axi0_ar_prot_o,
  output logic [ 3:0]                   core2axi0_ar_region_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi0_ar_user_o,
  output logic [ 3:0]                   core2axi0_ar_qos_o,
  output logic                          core2axi0_ar_valid_o,
  input  logic                          core2axi0_ar_ready_i,
  input  logic [AXI4_ID_WIDTH-1:0]      core2axi0_r_id_i,
  input  logic [AXI4_RDATA_WIDTH-1:0]   core2axi0_r_data_i,
  input  logic [ 1:0]                   core2axi0_r_resp_i,
  input  logic                          core2axi0_r_last_i,
  input  logic [AXI4_USER_WIDTH-1:0]    core2axi0_r_user_i,
  input  logic                          core2axi0_r_valid_i,
  output logic                          core2axi0_r_ready_o,

  // Core2AXI 1 - AXI Master interface (replaces SPI)
  output logic [AXI4_ID_WIDTH-1:0]      core2axi1_aw_id_o,
  output logic [AXI4_ADDRESS_WIDTH-1:0] core2axi1_aw_addr_o,
  output logic [ 7:0]                   core2axi1_aw_len_o,
  output logic [ 2:0]                   core2axi1_aw_size_o,
  output logic [ 1:0]                   core2axi1_aw_burst_o,
  output logic                          core2axi1_aw_lock_o,
  output logic [ 3:0]                   core2axi1_aw_cache_o,
  output logic [ 2:0]                   core2axi1_aw_prot_o,
  output logic [ 3:0]                   core2axi1_aw_region_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi1_aw_user_o,
  output logic [ 3:0]                   core2axi1_aw_qos_o,
  output logic                          core2axi1_aw_valid_o,
  input  logic                          core2axi1_aw_ready_i,
  output logic [AXI4_WDATA_WIDTH-1:0]   core2axi1_w_data_o,
  output logic [AXI4_WDATA_WIDTH/8-1:0] core2axi1_w_strb_o,
  output logic                          core2axi1_w_last_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi1_w_user_o,
  output logic                          core2axi1_w_valid_o,
  input  logic                          core2axi1_w_ready_i,
  input  logic [AXI4_ID_WIDTH-1:0]      core2axi1_b_id_i,
  input  logic [ 1:0]                   core2axi1_b_resp_i,
  input  logic                          core2axi1_b_valid_i,
  input  logic [AXI4_USER_WIDTH-1:0]    core2axi1_b_user_i,
  output logic                          core2axi1_b_ready_o,
  output logic [AXI4_ID_WIDTH-1:0]      core2axi1_ar_id_o,
  output logic [AXI4_ADDRESS_WIDTH-1:0] core2axi1_ar_addr_o,
  output logic [ 7:0]                   core2axi1_ar_len_o,
  output logic [ 2:0]                   core2axi1_ar_size_o,
  output logic [ 1:0]                   core2axi1_ar_burst_o,
  output logic                          core2axi1_ar_lock_o,
  output logic [ 3:0]                   core2axi1_ar_cache_o,
  output logic [ 2:0]                   core2axi1_ar_prot_o,
  output logic [ 3:0]                   core2axi1_ar_region_o,
  output logic [AXI4_USER_WIDTH-1:0]    core2axi1_ar_user_o,
  output logic [ 3:0]                   core2axi1_ar_qos_o,
  output logic                          core2axi1_ar_valid_o,
  input  logic                          core2axi1_ar_ready_i,
  input  logic [AXI4_ID_WIDTH-1:0]      core2axi1_r_id_i,
  input  logic [AXI4_RDATA_WIDTH-1:0]   core2axi1_r_data_i,
  input  logic [ 1:0]                   core2axi1_r_resp_i,
  input  logic                          core2axi1_r_last_i,
  input  logic [AXI4_USER_WIDTH-1:0]    core2axi1_r_user_i,
  input  logic                          core2axi1_r_valid_i,
  output logic                          core2axi1_r_ready_o,

  input  logic        tck_i,    // JTAG test clock pad
  input  logic        tms_i,    // JTAG test mode select pad
  input  logic        trst_ni,  // JTAG test reset pad
  input  logic        td_i,     // JTAG test data input pad
  output logic        td_o      // JTAG test data output pad
);
  localparam logic [31:0] MEM_SIZE      = 128 * 1024; // 128 KiB
  localparam logic [31:0] MEM_START     = 32'h00100000;
  localparam logic [31:0] MEM_MASK      = ~(MEM_SIZE-1);

  localparam logic [31:0] CORE2AXI0_SIZE  =  4 * 1024; //  4 KiB (replaces GPIO)
  localparam logic [31:0] CORE2AXI0_START = 32'h80000000;
  localparam logic [31:0] CORE2AXI0_MASK  = ~(CORE2AXI0_SIZE-1);

  localparam logic [31:0] DEBUG_SIZE    = 64 * 1024; // 64 KiB
  localparam logic [31:0] DEBUG_START   = 32'h1a110000;
  localparam logic [31:0] DEBUG_MASK    = ~(DEBUG_SIZE-1);

  localparam logic [31:0] UART_SIZE     =  4 * 1024; //  4 KiB
  localparam logic [31:0] UART_START    = 32'h80001000;
  localparam logic [31:0] UART_MASK     = ~(UART_SIZE-1);

  localparam logic [31:0] TIMER_SIZE    =  4 * 1024; //  4 KiB
  localparam logic [31:0] TIMER_START   = 32'h80002000;
  localparam logic [31:0] TIMER_MASK    = ~(TIMER_SIZE-1);

  localparam logic [31:0] PWM_SIZE      =  4 * 1024; //  4 KiB
  localparam logic [31:0] PWM_START     = 32'h80003000;
  localparam logic [31:0] PWM_MASK      = ~(PWM_SIZE-1);
  localparam int PwmCtrSize = 8;

  localparam logic [31:0] CORE2AXI1_SIZE  =  4 * 1024; //  4 KiB (replaces SPI)
  localparam logic [31:0] CORE2AXI1_START = 32'h80004000;
  localparam logic [31:0] CORE2AXI1_MASK  = ~(CORE2AXI1_SIZE-1);

  parameter logic [31:0] SIM_CTRL_SIZE  =  1 * 1024; //  1 KiB
  parameter logic [31:0] SIM_CTRL_START = 32'h20000;
  parameter logic [31:0] SIM_CTRL_MASK  = ~(SIM_CTRL_SIZE-1);

  // Debug functionality is optional.
  localparam bit DBG = 1;
  localparam int unsigned DbgHwBreakNum = (DBG == 1) ?    2 :    0;
  localparam bit          DbgTriggerEn  = (DBG == 1) ? 1'b1 : 1'b0;

  typedef enum int {
    CoreD,
    DbgHost
  } bus_host_e;

  typedef enum int {
    Ram,
    Core2Axi0,
    Pwm,
    Uart,
    Timer,
    Core2Axi1,
    SimCtrl,
    DbgDev
  } bus_device_e;

  localparam int NrDevices = DBG ? 8 : 7;
  localparam int NrHosts   = DBG ? 2 : 1;

  // Interrupts.
  logic timer_irq;
  logic uart_irq;

  // Host signals.
  logic        host_req      [NrHosts];
  logic        host_gnt      [NrHosts];
  logic [31:0] host_addr     [NrHosts];
  logic        host_we       [NrHosts];
  logic [ 3:0] host_be       [NrHosts];
  logic [31:0] host_wdata    [NrHosts];
  logic        host_rvalid   [NrHosts];
  logic [31:0] host_rdata    [NrHosts];
  logic        host_err      [NrHosts];

  // Device signals.
  logic        device_req    [NrDevices];
  logic [31:0] device_addr   [NrDevices];
  logic        device_we     [NrDevices];
  logic [ 3:0] device_be     [NrDevices];
  logic [31:0] device_wdata  [NrDevices];
  logic        device_rvalid [NrDevices];
  logic [31:0] device_rdata  [NrDevices];
  logic        device_err    [NrDevices];

  // Instruction fetch signals.
  logic        core_instr_req;
  logic        core_instr_gnt;
  logic        core_instr_rvalid;
  logic [31:0] core_instr_addr;
  logic [31:0] core_instr_rdata;
  logic        core_instr_sel_dbg;

  logic        mem_instr_req;
  logic [31:0] mem_instr_rdata;
  logic        dbg_instr_req;

  logic        dbg_device_req;
  logic [31:0] dbg_device_addr;
  logic        dbg_device_we;
  logic [ 3:0] dbg_device_be;
  logic [31:0] dbg_device_wdata;
  logic        dbg_device_rvalid;
  logic [31:0] dbg_device_rdata;

  // Internally generated resets cause IMPERFECTSCH warnings
  /* verilator lint_off IMPERFECTSCH */
  logic rst_core_n;
  logic ndmreset_req;
  logic dm_debug_req;

  // Device address mapping.
  logic [31:0] cfg_device_addr_base [NrDevices];
  logic [31:0] cfg_device_addr_mask [NrDevices];

  assign cfg_device_addr_base[Ram]       = MEM_START;
  assign cfg_device_addr_mask[Ram]       = MEM_MASK;
  assign cfg_device_addr_base[Core2Axi0] = CORE2AXI0_START;
  assign cfg_device_addr_mask[Core2Axi0] = CORE2AXI0_MASK;
  assign cfg_device_addr_base[Pwm]       = PWM_START;
  assign cfg_device_addr_mask[Pwm]       = PWM_MASK;
  assign cfg_device_addr_base[Uart]      = UART_START;
  assign cfg_device_addr_mask[Uart]      = UART_MASK;
  assign cfg_device_addr_base[Timer]     = TIMER_START;
  assign cfg_device_addr_mask[Timer]     = TIMER_MASK;
  assign cfg_device_addr_base[Core2Axi1] = CORE2AXI1_START;
  assign cfg_device_addr_mask[Core2Axi1] = CORE2AXI1_MASK;
  assign cfg_device_addr_base[SimCtrl]   = SIM_CTRL_START;
  assign cfg_device_addr_mask[SimCtrl]   = SIM_CTRL_MASK;

  if (DBG) begin : g_dbg_device_cfg
    assign cfg_device_addr_base[DbgDev] = DEBUG_START;
    assign cfg_device_addr_mask[DbgDev] = DEBUG_MASK;
    assign device_err[DbgDev] = 1'b0;
  end

  // Tie-off unused error signals.
  assign device_err[Ram]       = 1'b0;
  assign device_err[Core2Axi0] = 1'b0;
  assign device_err[Pwm]       = 1'b0;
  assign device_err[Uart]      = 1'b0;
  assign device_err[Core2Axi1] = 1'b0;
  assign device_err[SimCtrl]   = 1'b0;

  bus #(
    .NrDevices    ( NrDevices ),
    .NrHosts      ( NrHosts   ),
    .DataWidth    ( 32        ),
    .AddressWidth ( 32        )
  ) u_bus (
    .clk_i (clk_sys_i),
    .rst_ni(rst_sys_ni),

    .host_req_i   (host_req     ),
    .host_gnt_o   (host_gnt     ),
    .host_addr_i  (host_addr    ),
    .host_we_i    (host_we      ),
    .host_be_i    (host_be      ),
    .host_wdata_i (host_wdata   ),
    .host_rvalid_o(host_rvalid  ),
    .host_rdata_o (host_rdata   ),
    .host_err_o   (host_err     ),

    .device_req_o   (device_req   ),
    .device_addr_o  (device_addr  ),
    .device_we_o    (device_we    ),
    .device_be_o    (device_be    ),
    .device_wdata_o (device_wdata ),
    .device_rvalid_i(device_rvalid),
    .device_rdata_i (device_rdata ),
    .device_err_i   (device_err   ),

    .cfg_device_addr_base,
    .cfg_device_addr_mask
  );

  assign mem_instr_req =
      core_instr_req & ((core_instr_addr & cfg_device_addr_mask[Ram]) == cfg_device_addr_base[Ram]);

  assign dbg_instr_req =
      core_instr_req & ((core_instr_addr & cfg_device_addr_mask[DbgDev]) == cfg_device_addr_base[DbgDev]);

  assign core_instr_gnt = mem_instr_req | (dbg_instr_req & ~device_req[DbgDev]);

  always @(posedge clk_sys_i or negedge rst_sys_ni) begin
    if (!rst_sys_ni) begin
      core_instr_rvalid  <= 1'b0;
      core_instr_sel_dbg <= 1'b0;
    end else begin
      core_instr_rvalid  <= core_instr_gnt;
      core_instr_sel_dbg <= dbg_instr_req;
    end
  end

  assign core_instr_rdata = core_instr_sel_dbg ? dbg_device_rdata : mem_instr_rdata;

  assign rst_core_n = rst_sys_ni & ~ndmreset_req;

  // CV32E40PX interrupt bus - combining timer and UART interrupts
  logic [31:0] cv32_irq_bus;
  assign cv32_irq_bus = {19'b0, timer_irq, 11'b0, uart_irq};

  // CV32E40PX CORE-V-XIF signals (tied off - not used)
  logic                                         x_compressed_valid;
  logic                                         x_compressed_ready;
  cv32e40px_core_v_xif_pkg::x_compressed_req_t  x_compressed_req;
  cv32e40px_core_v_xif_pkg::x_compressed_resp_t x_compressed_resp;
  logic                                         x_issue_valid;
  logic                                         x_issue_ready;
  cv32e40px_core_v_xif_pkg::x_issue_req_t       x_issue_req;
  cv32e40px_core_v_xif_pkg::x_issue_resp_t      x_issue_resp;
  logic                                         x_commit_valid;
  cv32e40px_core_v_xif_pkg::x_commit_t          x_commit;
  logic                                         x_mem_valid;
  logic                                         x_mem_ready;
  cv32e40px_core_v_xif_pkg::x_mem_req_t         x_mem_req;
  cv32e40px_core_v_xif_pkg::x_mem_resp_t        x_mem_resp;
  logic                                         x_mem_result_valid;
  cv32e40px_core_v_xif_pkg::x_mem_result_t      x_mem_result;
  logic                                         x_result_valid;
  logic                                         x_result_ready;
  cv32e40px_core_v_xif_pkg::x_result_t          x_result;

  // Tie off CORE-V-XIF inputs
  assign x_compressed_ready = 1'b0;
  assign x_compressed_resp  = '0;
  assign x_issue_ready      = 1'b0;
  assign x_issue_resp       = '0;
  assign x_mem_valid        = 1'b0;
  assign x_mem_req          = '0;
  assign x_result_valid     = 1'b0;
  assign x_result           = '0;

  cv32e40px_top #(
    .COREV_X_IF       ( 0  ),
    .COREV_PULP       ( 0  ),
    .COREV_CLUSTER    ( 0  ),
    .FPU              ( 0  ),
    .FPU_ADDMUL_LAT   ( 0  ),
    .FPU_OTHERS_LAT   ( 0  ),
    .ZFINX            ( 0  ),
    .NUM_MHPMCOUNTERS ( 10 )
  ) u_top (
    .clk_i (clk_sys_i),
    .rst_ni(rst_core_n),

    .pulp_clock_en_i(1'b1),
    .scan_cg_en_i   (1'b0),

    .boot_addr_i        (32'h00100000),
    .mtvec_addr_i       (32'h00100000),
    .dm_halt_addr_i     (DEBUG_START + dm::HaltAddress[31:0]),
    .hart_id_i          (32'b0),
    .dm_exception_addr_i(DEBUG_START + dm::ExceptionAddress[31:0]),

    .instr_req_o   (core_instr_req),
    .instr_gnt_i   (core_instr_gnt),
    .instr_rvalid_i(core_instr_rvalid),
    .instr_addr_o  (core_instr_addr),
    .instr_rdata_i (core_instr_rdata),

    .data_req_o   (host_req[CoreD]),
    .data_gnt_i   (host_gnt[CoreD]),
    .data_rvalid_i(host_rvalid[CoreD]),
    .data_we_o    (host_we[CoreD]),
    .data_be_o    (host_be[CoreD]),
    .data_addr_o  (host_addr[CoreD]),
    .data_wdata_o (host_wdata[CoreD]),
    .data_rdata_i (host_rdata[CoreD]),

    // CORE-V-XIF interface (tied off)
    .x_compressed_valid_o(x_compressed_valid),
    .x_compressed_ready_i(x_compressed_ready),
    .x_compressed_req_o  (x_compressed_req),
    .x_compressed_resp_i (x_compressed_resp),
    .x_issue_valid_o     (x_issue_valid),
    .x_issue_ready_i     (x_issue_ready),
    .x_issue_req_o       (x_issue_req),
    .x_issue_resp_i      (x_issue_resp),
    .x_commit_valid_o    (x_commit_valid),
    .x_commit_o          (x_commit),
    .x_mem_valid_i       (x_mem_valid),
    .x_mem_ready_o       (x_mem_ready),
    .x_mem_req_i         (x_mem_req),
    .x_mem_resp_o        (x_mem_resp),
    .x_mem_result_valid_o(x_mem_result_valid),
    .x_mem_result_o      (x_mem_result),
    .x_result_valid_i    (x_result_valid),
    .x_result_ready_o    (x_result_ready),
    .x_result_i          (x_result),

    .irq_i    (cv32_irq_bus),
    .irq_ack_o(),
    .irq_id_o (),

    .debug_req_i      (dm_debug_req),
    .debug_havereset_o(),
    .debug_running_o  (),
    .debug_halted_o   (),

    .fetch_enable_i('1),
    .core_sleep_o  ()
  );

  ram_2p #(
      .Depth       ( MEM_SIZE / 4 ),
      .MemInitFile ( SRAMInitFile )
  ) u_ram (
    .clk_i (clk_sys_i),
    .rst_ni(rst_sys_ni),

    .a_req_i   (device_req[Ram]),
    .a_we_i    (device_we[Ram]),
    .a_be_i    (device_be[Ram]),
    .a_addr_i  (device_addr[Ram]),
    .a_wdata_i (device_wdata[Ram]),
    .a_rvalid_o(device_rvalid[Ram]),
    .a_rdata_o (device_rdata[Ram]),

    .b_req_i   (mem_instr_req),
    .b_we_i    (1'b0),
    .b_be_i    (4'b0),
    .b_addr_i  (core_instr_addr),
    .b_wdata_i (32'b0),
    .b_rvalid_o(),
    .b_rdata_o (mem_instr_rdata)
  );

  // Core2AXI Bridge 0 (replaces GPIO)
  // Users can connect their own AXI slave to this interface
  core2axi #(
    .AXI4_ADDRESS_WIDTH ( AXI4_ADDRESS_WIDTH ),
    .AXI4_RDATA_WIDTH   ( AXI4_RDATA_WIDTH   ),
    .AXI4_WDATA_WIDTH   ( AXI4_WDATA_WIDTH   ),
    .AXI4_ID_WIDTH      ( AXI4_ID_WIDTH      ),
    .AXI4_USER_WIDTH    ( AXI4_USER_WIDTH    ),
    .REGISTERED_GRANT   ( "FALSE"            )
  ) u_core2axi0 (
    .clk_i  (clk_sys_i),
    .rst_ni (rst_sys_ni),

    // Core protocol interface (connected to system bus)
    .data_req_i    (device_req[Core2Axi0]),
    .data_gnt_o    (/* unused - combinational grant */),
    .data_rvalid_o (device_rvalid[Core2Axi0]),
    .data_addr_i   (device_addr[Core2Axi0]),
    .data_we_i     (device_we[Core2Axi0]),
    .data_be_i     (device_be[Core2Axi0]),
    .data_rdata_o  (device_rdata[Core2Axi0]),
    .data_wdata_i  (device_wdata[Core2Axi0]),

    // AXI Master interface
    .aw_id_o     (core2axi0_aw_id_o),
    .aw_addr_o   (core2axi0_aw_addr_o),
    .aw_len_o    (core2axi0_aw_len_o),
    .aw_size_o   (core2axi0_aw_size_o),
    .aw_burst_o  (core2axi0_aw_burst_o),
    .aw_lock_o   (core2axi0_aw_lock_o),
    .aw_cache_o  (core2axi0_aw_cache_o),
    .aw_prot_o   (core2axi0_aw_prot_o),
    .aw_region_o (core2axi0_aw_region_o),
    .aw_user_o   (core2axi0_aw_user_o),
    .aw_qos_o    (core2axi0_aw_qos_o),
    .aw_valid_o  (core2axi0_aw_valid_o),
    .aw_ready_i  (core2axi0_aw_ready_i),
    .w_data_o    (core2axi0_w_data_o),
    .w_strb_o    (core2axi0_w_strb_o),
    .w_last_o    (core2axi0_w_last_o),
    .w_user_o    (core2axi0_w_user_o),
    .w_valid_o   (core2axi0_w_valid_o),
    .w_ready_i   (core2axi0_w_ready_i),
    .b_id_i      (core2axi0_b_id_i),
    .b_resp_i    (core2axi0_b_resp_i),
    .b_valid_i   (core2axi0_b_valid_i),
    .b_user_i    (core2axi0_b_user_i),
    .b_ready_o   (core2axi0_b_ready_o),
    .ar_id_o     (core2axi0_ar_id_o),
    .ar_addr_o   (core2axi0_ar_addr_o),
    .ar_len_o    (core2axi0_ar_len_o),
    .ar_size_o   (core2axi0_ar_size_o),
    .ar_burst_o  (core2axi0_ar_burst_o),
    .ar_lock_o   (core2axi0_ar_lock_o),
    .ar_cache_o  (core2axi0_ar_cache_o),
    .ar_prot_o   (core2axi0_ar_prot_o),
    .ar_region_o (core2axi0_ar_region_o),
    .ar_user_o   (core2axi0_ar_user_o),
    .ar_qos_o    (core2axi0_ar_qos_o),
    .ar_valid_o  (core2axi0_ar_valid_o),
    .ar_ready_i  (core2axi0_ar_ready_i),
    .r_id_i      (core2axi0_r_id_i),
    .r_data_i    (core2axi0_r_data_i),
    .r_resp_i    (core2axi0_r_resp_i),
    .r_last_i    (core2axi0_r_last_i),
    .r_user_i    (core2axi0_r_user_i),
    .r_valid_i   (core2axi0_r_valid_i),
    .r_ready_o   (core2axi0_r_ready_o)
  );

  pwm_wrapper #(
    .PwmWidth     ( PwmWidth   ),
    .PwmCtrSize   ( PwmCtrSize ),
    .BusAddrWidth ( 32         )
  ) u_pwm (
    .clk_i (clk_sys_i),
    .rst_ni(rst_sys_ni),

    .device_req_i   (device_req[Pwm]),
    .device_addr_i  (device_addr[Pwm]),
    .device_we_i    (device_we[Pwm]),
    .device_be_i    (device_be[Pwm]),
    .device_wdata_i (device_wdata[Pwm]),
    .device_rvalid_o(device_rvalid[Pwm]),
    .device_rdata_o (device_rdata[Pwm]),

    .pwm_o
  );

  uart #(
    .ClockFrequency ( ClockFrequency ),
    .BaudRate       ( BaudRate       )
  ) u_uart (
    .clk_i (clk_sys_i),
    .rst_ni(rst_sys_ni),

    .device_req_i   (device_req[Uart]),
    .device_addr_i  (device_addr[Uart]),
    .device_we_i    (device_we[Uart]),
    .device_be_i    (device_be[Uart]),
    .device_wdata_i (device_wdata[Uart]),
    .device_rvalid_o(device_rvalid[Uart]),
    .device_rdata_o (device_rdata[Uart]),

    .uart_rx_i,
    .uart_irq_o     (uart_irq),
    .uart_tx_o
  );

  // Core2AXI Bridge 1 (replaces SPI)
  // Users can connect their own AXI slave to this interface
  core2axi #(
    .AXI4_ADDRESS_WIDTH ( AXI4_ADDRESS_WIDTH ),
    .AXI4_RDATA_WIDTH   ( AXI4_RDATA_WIDTH   ),
    .AXI4_WDATA_WIDTH   ( AXI4_WDATA_WIDTH   ),
    .AXI4_ID_WIDTH      ( AXI4_ID_WIDTH      ),
    .AXI4_USER_WIDTH    ( AXI4_USER_WIDTH    ),
    .REGISTERED_GRANT   ( "FALSE"            )
  ) u_core2axi1 (
    .clk_i  (clk_sys_i),
    .rst_ni (rst_sys_ni),

    // Core protocol interface (connected to system bus)
    .data_req_i    (device_req[Core2Axi1]),
    .data_gnt_o    (/* unused - combinational grant */),
    .data_rvalid_o (device_rvalid[Core2Axi1]),
    .data_addr_i   (device_addr[Core2Axi1]),
    .data_we_i     (device_we[Core2Axi1]),
    .data_be_i     (device_be[Core2Axi1]),
    .data_rdata_o  (device_rdata[Core2Axi1]),
    .data_wdata_i  (device_wdata[Core2Axi1]),

    // AXI Master interface
    .aw_id_o     (core2axi1_aw_id_o),
    .aw_addr_o   (core2axi1_aw_addr_o),
    .aw_len_o    (core2axi1_aw_len_o),
    .aw_size_o   (core2axi1_aw_size_o),
    .aw_burst_o  (core2axi1_aw_burst_o),
    .aw_lock_o   (core2axi1_aw_lock_o),
    .aw_cache_o  (core2axi1_aw_cache_o),
    .aw_prot_o   (core2axi1_aw_prot_o),
    .aw_region_o (core2axi1_aw_region_o),
    .aw_user_o   (core2axi1_aw_user_o),
    .aw_qos_o    (core2axi1_aw_qos_o),
    .aw_valid_o  (core2axi1_aw_valid_o),
    .aw_ready_i  (core2axi1_aw_ready_i),
    .w_data_o    (core2axi1_w_data_o),
    .w_strb_o    (core2axi1_w_strb_o),
    .w_last_o    (core2axi1_w_last_o),
    .w_user_o    (core2axi1_w_user_o),
    .w_valid_o   (core2axi1_w_valid_o),
    .w_ready_i   (core2axi1_w_ready_i),
    .b_id_i      (core2axi1_b_id_i),
    .b_resp_i    (core2axi1_b_resp_i),
    .b_valid_i   (core2axi1_b_valid_i),
    .b_user_i    (core2axi1_b_user_i),
    .b_ready_o   (core2axi1_b_ready_o),
    .ar_id_o     (core2axi1_ar_id_o),
    .ar_addr_o   (core2axi1_ar_addr_o),
    .ar_len_o    (core2axi1_ar_len_o),
    .ar_size_o   (core2axi1_ar_size_o),
    .ar_burst_o  (core2axi1_ar_burst_o),
    .ar_lock_o   (core2axi1_ar_lock_o),
    .ar_cache_o  (core2axi1_ar_cache_o),
    .ar_prot_o   (core2axi1_ar_prot_o),
    .ar_region_o (core2axi1_ar_region_o),
    .ar_user_o   (core2axi1_ar_user_o),
    .ar_qos_o    (core2axi1_ar_qos_o),
    .ar_valid_o  (core2axi1_ar_valid_o),
    .ar_ready_i  (core2axi1_ar_ready_i),
    .r_id_i      (core2axi1_r_id_i),
    .r_data_i    (core2axi1_r_data_i),
    .r_resp_i    (core2axi1_r_resp_i),
    .r_last_i    (core2axi1_r_last_i),
    .r_user_i    (core2axi1_r_user_i),
    .r_valid_i   (core2axi1_r_valid_i),
    .r_ready_o   (core2axi1_r_ready_o)
  );

  `ifdef VERILATOR
    simulator_ctrl #(
      .LogName ( "ibex_demo_system.log" )
    ) u_simulator_ctrl (
      .clk_i (clk_sys_i),
      .rst_ni(rst_sys_ni),

      .req_i   (device_req[SimCtrl]),
      .we_i    (device_we[SimCtrl]),
      .be_i    (device_be[SimCtrl]),
      .addr_i  (device_addr[SimCtrl]),
      .wdata_i (device_wdata[SimCtrl]),
      .rvalid_o(device_rvalid[SimCtrl]),
      .rdata_o (device_rdata[SimCtrl])
    );
  `endif

  timer #(
    .DataWidth    ( 32 ),
    .AddressWidth ( 32 )
  ) u_timer (
    .clk_i (clk_sys_i),
    .rst_ni(rst_sys_ni),

    .timer_req_i   (device_req[Timer]),
    .timer_we_i    (device_we[Timer]),
    .timer_be_i    (device_be[Timer]),
    .timer_addr_i  (device_addr[Timer]),
    .timer_wdata_i (device_wdata[Timer]),
    .timer_rvalid_o(device_rvalid[Timer]),
    .timer_rdata_o (device_rdata[Timer]),
    .timer_err_o   (device_err[Timer]),
    .timer_intr_o  (timer_irq)
  );

  assign dbg_device_req        = device_req[DbgDev] | dbg_instr_req;
  assign dbg_device_we         = device_req[DbgDev] & device_we[DbgDev];
  assign dbg_device_addr       = device_req[DbgDev] ? device_addr[DbgDev] : core_instr_addr;
  assign dbg_device_be         = device_be[DbgDev];
  assign dbg_device_wdata      = device_wdata[DbgDev];
  assign device_rvalid[DbgDev] = dbg_device_rvalid;
  assign device_rdata[DbgDev]  = dbg_device_rdata;

  always @(posedge clk_sys_i or negedge rst_sys_ni) begin
    if (!rst_sys_ni) begin
      dbg_device_rvalid <= 1'b0;
    end else begin
      dbg_device_rvalid <= device_req[DbgDev];
    end
  end

  if (DBG) begin : gen_dm_top
    dm_top #(
      .NrHarts      ( 1                              ),
      .IdcodeValue  ( jtag_id_pkg::RV_DM_JTAG_IDCODE )
    ) u_dm_top (
      .clk_i        (clk_sys_i),
      .rst_ni       (rst_sys_ni),
      .testmode_i   (1'b0),
      .ndmreset_o   (ndmreset_req),
      .dmactive_o   (),
      .debug_req_o  (dm_debug_req),
      .unavailable_i(1'b0),

      // Bus device with debug memory (for execution-based debug).
      .device_req_i  (dbg_device_req),
      .device_we_i   (dbg_device_we),
      .device_addr_i (dbg_device_addr),
      .device_be_i   (dbg_device_be),
      .device_wdata_i(dbg_device_wdata),
      .device_rdata_o(dbg_device_rdata),

      // Bus host (for system bus accesses, SBA).
      .host_req_o    (host_req[DbgHost]),
      .host_add_o    (host_addr[DbgHost]),
      .host_we_o     (host_we[DbgHost]),
      .host_wdata_o  (host_wdata[DbgHost]),
      .host_be_o     (host_be[DbgHost]),
      .host_gnt_i    (host_gnt[DbgHost]),
      .host_r_valid_i(host_rvalid[DbgHost]),
      .host_r_rdata_i(host_rdata[DbgHost]),

      .tck_i,
      .tms_i,
      .trst_ni,
      .td_i,
      .td_o
    );
  end else begin : gen_no_dm
    assign dm_debug_req = 1'b0;
    assign ndmreset_req = 1'b0;
  end

  `ifdef VERILATOR

    export "DPI-C" function mhpmcounter_num;

    function automatic int unsigned mhpmcounter_num();
      // CV32E40PX has NUM_MHPMCOUNTERS parameter (10 in this case)
      return 10;
    endfunction

    export "DPI-C" function mhpmcounter_get;

    function automatic longint unsigned mhpmcounter_get(int index);
      // CV32E40PX counter access - note the different hierarchy
      // The counters are in core_i.cs_registers_i
      return u_top.core_i.cs_registers_i.mhpmcounter_q[index];
    endfunction
  `endif
endmodule
