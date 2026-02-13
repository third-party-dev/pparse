console.log(JSON.stringify({
  objects: [
    {
      name: "tflite.ATan2Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.AbsOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.AddNOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.AddOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "pot_scale_int16",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6,
          default_integer: 1
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ArgMaxOptions",
      fields: [
        {
          name: "output_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ArgMinOptions",
      fields: [
        {
          name: "output_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.AssignVariableOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BatchMatMulOptions",
      fields: [
        {
          name: "adj_x",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "adj_y",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BatchToSpaceNDOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BidirectionalSequenceLSTMOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 5,
          offset: 14
        },
        {
          name: "cell_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "merge_outputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "proj_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "time_major",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12,
          default_integer: 1
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BidirectionalSequenceRNNOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "merge_outputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "time_major",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BitcastOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BitwiseXorOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BroadcastToOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.BucketizeOptions",
      fields: [
        {
          name: "boundaries",
          type: {
            base_type: "Vector",
            element: "Float",
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Buffer",
      fields: [
        {
          name: "data",
          type: {
            base_type: "Vector",
            element: "UByte",
            element_size: 1
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CallOnceOptions",
      fields: [
        {
          name: "init_subgraph_index",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CallOptions",
      fields: [
        {
          name: "subgraph",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CastOptions",
      fields: [
        {
          name: "in_data_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "out_data_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ConcatEmbeddingsOptions",
      fields: [
        {
          name: "embedding_dim_per_channel",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "num_channels",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "num_columns_per_channel",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ConcatenationOptions",
      fields: [
        {
          name: "axis",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Conv2DOptions",
      fields: [
        {
          name: "dilation_h_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 5,
          offset: 14,
          default_integer: 1
        },
        {
          name: "dilation_w_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 4,
          offset: 12,
          default_integer: 1
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "padding",
          type: {
            base_type: "Byte",
            index: 10,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "stride_h",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "stride_w",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Conv3DOptions",
      fields: [
        {
          name: "dilation_d_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 5,
          offset: 14,
          default_integer: 1
        },
        {
          name: "dilation_h_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 7,
          offset: 18,
          default_integer: 1
        },
        {
          name: "dilation_w_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 6,
          offset: 16,
          default_integer: 1
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "padding",
          type: {
            base_type: "Byte",
            index: 10,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "stride_d",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "stride_h",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "stride_w",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CosOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CumsumOptions",
      fields: [
        {
          name: "exclusive",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "reverse",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.CustomQuantization",
      fields: [
        {
          name: "custom",
          type: {
            base_type: "Vector",
            element: "UByte",
            element_size: 1
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DensifyOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DepthToSpaceOptions",
      fields: [
        {
          name: "block_size",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DepthwiseConv2DOptions",
      fields: [
        {
          name: "depth_multiplier",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "dilation_h_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 6,
          offset: 16,
          default_integer: 1
        },
        {
          name: "dilation_w_factor",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 5,
          offset: 14,
          default_integer: 1
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "padding",
          type: {
            base_type: "Byte",
            index: 10,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "stride_h",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "stride_w",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DequantizeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DimensionMetadata",
      fields: [
        {
          name: "array_indices",
          type: {
            base_type: "Union",
            index: 12,
            element_size: 1
          },
          id: 5,
          offset: 14,
          optional: true
        },
        {
          name: "array_indices_type",
          type: {
            base_type: "UType",
            index: 12,
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "array_segments",
          type: {
            base_type: "Union",
            index: 12,
            element_size: 1
          },
          id: 3,
          offset: 10,
          optional: true
        },
        {
          name: "array_segments_type",
          type: {
            base_type: "UType",
            index: 12,
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "dense_size",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "format",
          type: {
            base_type: "Byte",
            index: 5,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DivOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.DynamicUpdateSliceOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.EmbeddingLookupSparseOptions",
      fields: [
        {
          name: "combiner",
          type: {
            base_type: "Byte",
            index: 3,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.EqualOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ExpOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ExpandDimsOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.FakeQuantOptions",
      fields: [
        {
          name: "max",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "min",
          type: {
            base_type: "Float",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "narrow_range",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "num_bits",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.FillOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.FloorDivOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.FloorModOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.FullyConnectedOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "keep_num_dims",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "weights_format",
          type: {
            base_type: "Byte",
            index: 6,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.GatherNdOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.GatherOptions",
      fields: [
        {
          name: "axis",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "batch_dims",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.GeluOptions",
      fields: [
        {
          name: "approximate",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.GreaterEqualOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.GreaterOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.HardSwishOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.HashtableFindOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.HashtableImportOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.HashtableOptions",
      fields: [
        {
          name: "key_dtype",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "table_id",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "value_dtype",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.HashtableSizeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.IfOptions",
      fields: [
        {
          name: "else_subgraph_index",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "then_subgraph_index",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Int32Vector",
      fields: [
        {
          name: "values",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.L2NormOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LSHProjectionOptions",
      fields: [
        {
          name: "type",
          type: {
            base_type: "Byte",
            index: 7,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LSTMOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "cell_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "kernel_type",
          type: {
            base_type: "Byte",
            index: 8,
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "proj_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 2,
          offset: 8
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LeakyReluOptions",
      fields: [
        {
          name: "alpha",
          type: {
            base_type: "Float",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LessEqualOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LessOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LocalResponseNormalizationOptions",
      fields: [
        {
          name: "alpha",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "beta",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "bias",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "radius",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LogSoftmaxOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LogicalAndOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LogicalNotOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.LogicalOrOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.MatrixDiagOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.MatrixSetDiagOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.MaximumMinimumOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Metadata",
      fields: [
        {
          name: "buffer",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "name",
          type: {
            base_type: "String",
            element_size: 1
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.MirrorPadOptions",
      fields: [
        {
          name: "mode",
          type: {
            base_type: "Byte",
            index: 9,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Model",
      fields: [
        {
          name: "buffers",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 15,
            element_size: 4
          },
          id: 4,
          offset: 12,
          optional: true
        },
        {
          name: "description",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 3,
          offset: 10,
          optional: true
        },
        {
          name: "metadata",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 68,
            element_size: 4
          },
          id: 6,
          offset: 16,
          optional: true
        },
        {
          name: "metadata_buffer",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 5,
          offset: 14,
          optional: true
        },
        {
          name: "operator_codes",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 78,
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "signature_defs",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 107,
            element_size: 4
          },
          id: 7,
          offset: 18,
          optional: true
        },
        {
          name: "subgraphs",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 121,
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "version",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.MulOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.NegOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.NonMaxSuppressionV4Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.NonMaxSuppressionV5Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.NotEqualOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.OneHotOptions",
      fields: [
        {
          name: "axis",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Operator",
      fields: [
        {
          name: "builtin_options",
          type: {
            base_type: "Union",
            index: 2,
            element_size: 1
          },
          id: 4,
          offset: 12,
          optional: true
        },
        {
          name: "builtin_options_type",
          type: {
            base_type: "UType",
            index: 2,
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "custom_options",
          type: {
            base_type: "Vector",
            element: "UByte",
            element_size: 1
          },
          id: 5,
          offset: 14,
          optional: true
        },
        {
          name: "custom_options_format",
          type: {
            base_type: "Byte",
            index: 4,
            base_size: 1,
            element_size: 1
          },
          id: 6,
          offset: 16
        },
        {
          name: "inputs",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "intermediates",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 8,
          offset: 20,
          optional: true
        },
        {
          name: "mutating_variable_inputs",
          type: {
            base_type: "Vector",
            element: "Bool",
            element_size: 1
          },
          id: 7,
          offset: 18,
          optional: true
        },
        {
          name: "opcode_index",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "outputs",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.OperatorCode",
      fields: [
        {
          name: "builtin_code",
          type: {
            base_type: "Int",
            index: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "custom_code",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "deprecated_builtin_code",
          type: {
            base_type: "Byte",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "version",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8,
          default_integer: 1
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.PackOptions",
      fields: [
        {
          name: "axis",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "values_count",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.PadOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.PadV2Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Pool2DOptions",
      fields: [
        {
          name: "filter_height",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "filter_width",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 5,
          offset: 14
        },
        {
          name: "padding",
          type: {
            base_type: "Byte",
            index: 10,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "stride_h",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "stride_w",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.PowOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.QuantizationParameters",
      fields: [
        {
          name: "details",
          type: {
            base_type: "Union",
            index: 11,
            element_size: 1
          },
          id: 5,
          offset: 14,
          optional: true
        },
        {
          name: "details_type",
          type: {
            base_type: "UType",
            index: 11,
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "max",
          type: {
            base_type: "Vector",
            element: "Float",
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "min",
          type: {
            base_type: "Vector",
            element: "Float",
            element_size: 4
          },
          offset: 4,
          optional: true
        },
        {
          name: "quantized_dimension",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 6,
          offset: 16
        },
        {
          name: "scale",
          type: {
            base_type: "Vector",
            element: "Float",
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "zero_point",
          type: {
            base_type: "Vector",
            element: "Long",
            element_size: 8
          },
          id: 3,
          offset: 10,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.QuantizeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.RNNOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.RandomOptions",
      fields: [
        {
          name: "seed",
          type: {
            base_type: "Long",
            base_size: 8,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "seed2",
          type: {
            base_type: "Long",
            base_size: 8,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.RangeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.RankOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ReadVariableOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ReducerOptions",
      fields: [
        {
          name: "keep_dims",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ReshapeOptions",
      fields: [
        {
          name: "new_shape",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ResizeBilinearOptions",
      fields: [
        {
          name: "align_corners",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "half_pixel_centers",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "new_height",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4,
          deprecated: true
        },
        {
          name: "new_width",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6,
          deprecated: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ResizeNearestNeighborOptions",
      fields: [
        {
          name: "align_corners",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "half_pixel_centers",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ReverseSequenceOptions",
      fields: [
        {
          name: "batch_dim",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "seq_dim",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ReverseV2Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Rfft2dOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.RightShiftOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SVDFOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "rank",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ScatterNdOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SegmentSumOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SelectOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SelectV2Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SequenceRNNOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "time_major",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ShapeOptions",
      fields: [
        {
          name: "out_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SignOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SignatureDef",
      fields: [
        {
          name: "deprecated_tag",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 3,
          offset: 10,
          deprecated: true,
          optional: true
        },
        {
          name: "inputs",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 124,
            element_size: 4
          },
          offset: 4,
          optional: true
        },
        {
          name: "outputs",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 124,
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "signature_key",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "subgraph_index",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          id: 4,
          offset: 12
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SkipGramOptions",
      fields: [
        {
          name: "include_all_ngrams",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "max_skip_size",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "ngram_size",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SliceOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SoftmaxOptions",
      fields: [
        {
          name: "beta",
          type: {
            base_type: "Float",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SpaceToBatchNDOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SpaceToDepthOptions",
      fields: [
        {
          name: "block_size",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SparseToDenseOptions",
      fields: [
        {
          name: "validate_indices",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SparsityParameters",
      fields: [
        {
          name: "block_map",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "dim_metadata",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 30,
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "traversal_order",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SplitOptions",
      fields: [
        {
          name: "num_splits",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SplitVOptions",
      fields: [
        {
          name: "num_splits",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SquareOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SquaredDifferenceOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SqueezeOptions",
      fields: [
        {
          name: "squeeze_dims",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.StridedSliceOptions",
      fields: [
        {
          name: "begin_mask",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        },
        {
          name: "ellipsis_mask",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "end_mask",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "new_axis_mask",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "shrink_axis_mask",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 4,
          offset: 12
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SubGraph",
      fields: [
        {
          name: "inputs",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 1,
          offset: 6,
          optional: true
        },
        {
          name: "name",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 4,
          offset: 12,
          optional: true
        },
        {
          name: "operators",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 77,
            element_size: 4
          },
          id: 3,
          offset: 10,
          optional: true
        },
        {
          name: "outputs",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 2,
          offset: 8,
          optional: true
        },
        {
          name: "tensors",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 123,
            element_size: 4
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.SubOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "pot_scale_int16",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6,
          default_integer: 1
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Tensor",
      fields: [
        {
          name: "buffer",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "has_rank",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 8,
          offset: 20
        },
        {
          name: "is_variable",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 5,
          offset: 14
        },
        {
          name: "name",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 3,
          offset: 10,
          optional: true
        },
        {
          name: "quantization",
          type: {
            base_type: "Obj",
            index: 84,
            element_size: 1
          },
          id: 4,
          offset: 12,
          optional: true
        },
        {
          name: "shape",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        },
        {
          name: "shape_signature",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          id: 7,
          offset: 18,
          optional: true
        },
        {
          name: "sparsity",
          type: {
            base_type: "Obj",
            index: 114,
            element_size: 1
          },
          id: 6,
          offset: 16,
          optional: true
        },
        {
          name: "type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "variant_tensors",
          type: {
            base_type: "Vector",
            element: "Obj",
            index: 139,
            element_size: 4
          },
          id: 9,
          offset: 22,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.TensorMap",
      fields: [
        {
          name: "name",
          type: {
            base_type: "String",
            element_size: 1
          },
          offset: 4,
          optional: true
        },
        {
          name: "tensor_index",
          type: {
            base_type: "UInt",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.TileOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.TopKV2Options",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.TransposeConvOptions",
      fields: [
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        },
        {
          name: "padding",
          type: {
            base_type: "Byte",
            index: 10,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "stride_h",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "stride_w",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.TransposeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Uint16Vector",
      fields: [
        {
          name: "values",
          type: {
            base_type: "Vector",
            element: "UShort",
            element_size: 2
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.Uint8Vector",
      fields: [
        {
          name: "values",
          type: {
            base_type: "Vector",
            element: "UByte",
            element_size: 1
          },
          offset: 4,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnidirectionalSequenceLSTMOptions",
      fields: [
        {
          name: "asymmetric_quantize_inputs",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 4,
          offset: 12
        },
        {
          name: "cell_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "diagonal_recurrent_tensors",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 5,
          offset: 14
        },
        {
          name: "fused_activation_function",
          type: {
            base_type: "Byte",
            index: 0,
            base_size: 1,
            element_size: 1
          },
          offset: 4
        },
        {
          name: "proj_clip",
          type: {
            base_type: "Float",
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "time_major",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 3,
          offset: 10
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UniqueOptions",
      fields: [
        {
          name: "idx_out_type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          offset: 4,
          default_integer: 2
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnpackOptions",
      fields: [
        {
          name: "axis",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "num",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnsortedSegmentMaxOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnsortedSegmentMinOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnsortedSegmentProdOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.UnsortedSegmentSumOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.VarHandleOptions",
      fields: [
        {
          name: "container",
          type: {
            base_type: "String",
            element_size: 1
          },
          offset: 4,
          optional: true
        },
        {
          name: "shared_name",
          type: {
            base_type: "String",
            element_size: 1
          },
          id: 1,
          offset: 6,
          optional: true
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.VariantSubType",
      fields: [
        {
          name: "has_rank",
          type: {
            base_type: "Bool",
            base_size: 1,
            element_size: 1
          },
          id: 2,
          offset: 8
        },
        {
          name: "shape",
          type: {
            base_type: "Vector",
            element: "Int",
            element_size: 4
          },
          offset: 4,
          optional: true
        },
        {
          name: "type",
          type: {
            base_type: "Byte",
            index: 13,
            base_size: 1,
            element_size: 1
          },
          id: 1,
          offset: 6
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.WhereOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.WhileOptions",
      fields: [
        {
          name: "body_subgraph_index",
          type: {
            base_type: "Int",
            element_size: 1
          },
          id: 1,
          offset: 6
        },
        {
          name: "cond_subgraph_index",
          type: {
            base_type: "Int",
            element_size: 1
          },
          offset: 4
        }
      ],
      minalign: 1,
      declaration_file: ""
    },
    {
      name: "tflite.ZerosLikeOptions",
      fields: [

      ],
      minalign: 1,
      declaration_file: ""
    }
  ],
  enums: [
    {
      name: "tflite.ActivationFunctionType",
      values: [
        {
          name: "NONE",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU_N1_TO_1",
          value: 2,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU6",
          value: 3,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TANH",
          value: 4,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SIGN_BIT",
          value: 5,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 0,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.BuiltinOperator",
      values: [
        {
          name: "ADD",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "AVERAGE_POOL_2D",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CONCATENATION",
          value: 2,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CONV_2D",
          value: 3,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DEPTHWISE_CONV_2D",
          value: 4,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DEPTH_TO_SPACE",
          value: 5,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DEQUANTIZE",
          value: 6,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "EMBEDDING_LOOKUP",
          value: 7,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FLOOR",
          value: 8,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FULLY_CONNECTED",
          value: 9,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HASHTABLE_LOOKUP",
          value: 10,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "L2_NORMALIZATION",
          value: 11,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "L2_POOL_2D",
          value: 12,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOCAL_RESPONSE_NORMALIZATION",
          value: 13,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOGISTIC",
          value: 14,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LSH_PROJECTION",
          value: 15,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LSTM",
          value: 16,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MAX_POOL_2D",
          value: 17,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MUL",
          value: 18,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU",
          value: 19,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU_N1_TO_1",
          value: 20,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU6",
          value: 21,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RESHAPE",
          value: 22,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RESIZE_BILINEAR",
          value: 23,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RNN",
          value: 24,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SOFTMAX",
          value: 25,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPACE_TO_DEPTH",
          value: 26,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SVDF",
          value: 27,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TANH",
          value: 28,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CONCAT_EMBEDDINGS",
          value: 29,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SKIP_GRAM",
          value: 30,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CALL",
          value: 31,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CUSTOM",
          value: 32,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "EMBEDDING_LOOKUP_SPARSE",
          value: 33,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "PAD",
          value: 34,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNIDIRECTIONAL_SEQUENCE_RNN",
          value: 35,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "GATHER",
          value: 36,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BATCH_TO_SPACE_ND",
          value: 37,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPACE_TO_BATCH_ND",
          value: 38,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TRANSPOSE",
          value: 39,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MEAN",
          value: 40,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SUB",
          value: 41,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DIV",
          value: 42,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SQUEEZE",
          value: 43,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNIDIRECTIONAL_SEQUENCE_LSTM",
          value: 44,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "STRIDED_SLICE",
          value: 45,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BIDIRECTIONAL_SEQUENCE_RNN",
          value: 46,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "EXP",
          value: 47,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TOPK_V2",
          value: 48,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPLIT",
          value: 49,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOG_SOFTMAX",
          value: 50,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DELEGATE",
          value: 51,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BIDIRECTIONAL_SEQUENCE_LSTM",
          value: 52,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CAST",
          value: 53,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "PRELU",
          value: 54,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MAXIMUM",
          value: 55,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ARG_MAX",
          value: 56,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MINIMUM",
          value: 57,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LESS",
          value: 58,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "NEG",
          value: 59,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "PADV2",
          value: 60,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "GREATER",
          value: 61,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "GREATER_EQUAL",
          value: 62,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LESS_EQUAL",
          value: 63,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SELECT",
          value: 64,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SLICE",
          value: 65,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SIN",
          value: 66,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TRANSPOSE_CONV",
          value: 67,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPARSE_TO_DENSE",
          value: 68,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "TILE",
          value: 69,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "EXPAND_DIMS",
          value: 70,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "EQUAL",
          value: 71,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "NOT_EQUAL",
          value: 72,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOG",
          value: 73,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SUM",
          value: 74,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SQRT",
          value: 75,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RSQRT",
          value: 76,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SHAPE",
          value: 77,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "POW",
          value: 78,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ARG_MIN",
          value: 79,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FAKE_QUANT",
          value: 80,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REDUCE_PROD",
          value: 81,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REDUCE_MAX",
          value: 82,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "PACK",
          value: 83,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOGICAL_OR",
          value: 84,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ONE_HOT",
          value: 85,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOGICAL_AND",
          value: 86,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LOGICAL_NOT",
          value: 87,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNPACK",
          value: 88,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REDUCE_MIN",
          value: 89,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FLOOR_DIV",
          value: 90,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REDUCE_ANY",
          value: 91,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SQUARE",
          value: 92,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ZEROS_LIKE",
          value: 93,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FILL",
          value: 94,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FLOOR_MOD",
          value: 95,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RANGE",
          value: 96,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RESIZE_NEAREST_NEIGHBOR",
          value: 97,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "LEAKY_RELU",
          value: 98,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SQUARED_DIFFERENCE",
          value: 99,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MIRROR_PAD",
          value: 100,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ABS",
          value: 101,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPLIT_V",
          value: 102,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNIQUE",
          value: 103,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CEIL",
          value: 104,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REVERSE_V2",
          value: 105,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ADD_N",
          value: 106,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "GATHER_ND",
          value: 107,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "COS",
          value: 108,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "WHERE",
          value: 109,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RANK",
          value: 110,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ELU",
          value: 111,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REVERSE_SEQUENCE",
          value: 112,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MATRIX_DIAG",
          value: 113,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "QUANTIZE",
          value: 114,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MATRIX_SET_DIAG",
          value: 115,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ROUND",
          value: 116,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HARD_SWISH",
          value: 117,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "IF",
          value: 118,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "WHILE",
          value: 119,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "NON_MAX_SUPPRESSION_V4",
          value: 120,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "NON_MAX_SUPPRESSION_V5",
          value: 121,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SCATTER_ND",
          value: 122,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SELECT_V2",
          value: 123,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DENSIFY",
          value: 124,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SEGMENT_SUM",
          value: 125,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BATCH_MATMUL",
          value: 126,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "PLACEHOLDER_FOR_GREATER_OP_CODES",
          value: 127,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CUMSUM",
          value: 128,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CALL_ONCE",
          value: 129,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BROADCAST_TO",
          value: 130,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RFFT2D",
          value: 131,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CONV_3D",
          value: 132,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "IMAG",
          value: 133,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REAL",
          value: 134,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "COMPLEX_ABS",
          value: 135,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HASHTABLE",
          value: 136,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HASHTABLE_FIND",
          value: 137,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HASHTABLE_IMPORT",
          value: 138,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "HASHTABLE_SIZE",
          value: 139,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "REDUCE_ALL",
          value: 140,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CONV_3D_TRANSPOSE",
          value: 141,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "VAR_HANDLE",
          value: 142,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "READ_VARIABLE",
          value: 143,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ASSIGN_VARIABLE",
          value: 144,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BROADCAST_ARGS",
          value: 145,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RANDOM_STANDARD_NORMAL",
          value: 146,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BUCKETIZE",
          value: 147,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RANDOM_UNIFORM",
          value: 148,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MULTINOMIAL",
          value: 149,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "GELU",
          value: 150,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DYNAMIC_UPDATE_SLICE",
          value: 151,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RELU_0_TO_1",
          value: 152,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNSORTED_SEGMENT_PROD",
          value: 153,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNSORTED_SEGMENT_MAX",
          value: 154,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNSORTED_SEGMENT_SUM",
          value: 155,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "ATAN2",
          value: 156,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UNSORTED_SEGMENT_MIN",
          value: 157,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SIGN",
          value: 158,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BITCAST",
          value: 159,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BITWISE_XOR",
          value: 160,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RIGHT_SHIFT",
          value: 161,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Int",
        index: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.BuiltinOptions",
      values: [
        {
          name: "NONE",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "Conv2DOptions",
          value: 1,
          union_type: {
            base_type: "Obj",
            index: 21,
            element_size: 1
          }
        },
        {
          name: "DepthwiseConv2DOptions",
          value: 2,
          union_type: {
            base_type: "Obj",
            index: 28,
            element_size: 1
          }
        },
        {
          name: "ConcatEmbeddingsOptions",
          value: 3,
          union_type: {
            base_type: "Obj",
            index: 19,
            element_size: 1
          }
        },
        {
          name: "LSHProjectionOptions",
          value: 4,
          union_type: {
            base_type: "Obj",
            index: 55,
            element_size: 1
          }
        },
        {
          name: "Pool2DOptions",
          value: 5,
          union_type: {
            base_type: "Obj",
            index: 82,
            element_size: 1
          }
        },
        {
          name: "SVDFOptions",
          value: 6,
          union_type: {
            base_type: "Obj",
            index: 99,
            element_size: 1
          }
        },
        {
          name: "RNNOptions",
          value: 7,
          union_type: {
            base_type: "Obj",
            index: 86,
            element_size: 1
          }
        },
        {
          name: "FullyConnectedOptions",
          value: 8,
          union_type: {
            base_type: "Obj",
            index: 41,
            element_size: 1
          }
        },
        {
          name: "SoftmaxOptions",
          value: 9,
          union_type: {
            base_type: "Obj",
            index: 110,
            element_size: 1
          }
        },
        {
          name: "ConcatenationOptions",
          value: 10,
          union_type: {
            base_type: "Obj",
            index: 20,
            element_size: 1
          }
        },
        {
          name: "AddOptions",
          value: 11,
          union_type: {
            base_type: "Obj",
            index: 3,
            element_size: 1
          }
        },
        {
          name: "L2NormOptions",
          value: 12,
          union_type: {
            base_type: "Obj",
            index: 54,
            element_size: 1
          }
        },
        {
          name: "LocalResponseNormalizationOptions",
          value: 13,
          union_type: {
            base_type: "Obj",
            index: 60,
            element_size: 1
          }
        },
        {
          name: "LSTMOptions",
          value: 14,
          union_type: {
            base_type: "Obj",
            index: 56,
            element_size: 1
          }
        },
        {
          name: "ResizeBilinearOptions",
          value: 15,
          union_type: {
            base_type: "Obj",
            index: 93,
            element_size: 1
          }
        },
        {
          name: "CallOptions",
          value: 16,
          union_type: {
            base_type: "Obj",
            index: 17,
            element_size: 1
          }
        },
        {
          name: "ReshapeOptions",
          value: 17,
          union_type: {
            base_type: "Obj",
            index: 92,
            element_size: 1
          }
        },
        {
          name: "SkipGramOptions",
          value: 18,
          union_type: {
            base_type: "Obj",
            index: 108,
            element_size: 1
          }
        },
        {
          name: "SpaceToDepthOptions",
          value: 19,
          union_type: {
            base_type: "Obj",
            index: 112,
            element_size: 1
          }
        },
        {
          name: "EmbeddingLookupSparseOptions",
          value: 20,
          union_type: {
            base_type: "Obj",
            index: 33,
            element_size: 1
          }
        },
        {
          name: "MulOptions",
          value: 21,
          union_type: {
            base_type: "Obj",
            index: 71,
            element_size: 1
          }
        },
        {
          name: "PadOptions",
          value: 22,
          union_type: {
            base_type: "Obj",
            index: 80,
            element_size: 1
          }
        },
        {
          name: "GatherOptions",
          value: 23,
          union_type: {
            base_type: "Obj",
            index: 43,
            element_size: 1
          }
        },
        {
          name: "BatchToSpaceNDOptions",
          value: 24,
          union_type: {
            base_type: "Obj",
            index: 8,
            element_size: 1
          }
        },
        {
          name: "SpaceToBatchNDOptions",
          value: 25,
          union_type: {
            base_type: "Obj",
            index: 111,
            element_size: 1
          }
        },
        {
          name: "TransposeOptions",
          value: 26,
          union_type: {
            base_type: "Obj",
            index: 128,
            element_size: 1
          }
        },
        {
          name: "ReducerOptions",
          value: 27,
          union_type: {
            base_type: "Obj",
            index: 91,
            element_size: 1
          }
        },
        {
          name: "SubOptions",
          value: 28,
          union_type: {
            base_type: "Obj",
            index: 122,
            element_size: 1
          }
        },
        {
          name: "DivOptions",
          value: 29,
          union_type: {
            base_type: "Obj",
            index: 31,
            element_size: 1
          }
        },
        {
          name: "SqueezeOptions",
          value: 30,
          union_type: {
            base_type: "Obj",
            index: 119,
            element_size: 1
          }
        },
        {
          name: "SequenceRNNOptions",
          value: 31,
          union_type: {
            base_type: "Obj",
            index: 104,
            element_size: 1
          }
        },
        {
          name: "StridedSliceOptions",
          value: 32,
          union_type: {
            base_type: "Obj",
            index: 120,
            element_size: 1
          }
        },
        {
          name: "ExpOptions",
          value: 33,
          union_type: {
            base_type: "Obj",
            index: 35,
            element_size: 1
          }
        },
        {
          name: "TopKV2Options",
          value: 34,
          union_type: {
            base_type: "Obj",
            index: 126,
            element_size: 1
          }
        },
        {
          name: "SplitOptions",
          value: 35,
          union_type: {
            base_type: "Obj",
            index: 115,
            element_size: 1
          }
        },
        {
          name: "LogSoftmaxOptions",
          value: 36,
          union_type: {
            base_type: "Obj",
            index: 61,
            element_size: 1
          }
        },
        {
          name: "CastOptions",
          value: 37,
          union_type: {
            base_type: "Obj",
            index: 18,
            element_size: 1
          }
        },
        {
          name: "DequantizeOptions",
          value: 38,
          union_type: {
            base_type: "Obj",
            index: 29,
            element_size: 1
          }
        },
        {
          name: "MaximumMinimumOptions",
          value: 39,
          union_type: {
            base_type: "Obj",
            index: 67,
            element_size: 1
          }
        },
        {
          name: "ArgMaxOptions",
          value: 40,
          union_type: {
            base_type: "Obj",
            index: 4,
            element_size: 1
          }
        },
        {
          name: "LessOptions",
          value: 41,
          union_type: {
            base_type: "Obj",
            index: 59,
            element_size: 1
          }
        },
        {
          name: "NegOptions",
          value: 42,
          union_type: {
            base_type: "Obj",
            index: 72,
            element_size: 1
          }
        },
        {
          name: "PadV2Options",
          value: 43,
          union_type: {
            base_type: "Obj",
            index: 81,
            element_size: 1
          }
        },
        {
          name: "GreaterOptions",
          value: 44,
          union_type: {
            base_type: "Obj",
            index: 46,
            element_size: 1
          }
        },
        {
          name: "GreaterEqualOptions",
          value: 45,
          union_type: {
            base_type: "Obj",
            index: 45,
            element_size: 1
          }
        },
        {
          name: "LessEqualOptions",
          value: 46,
          union_type: {
            base_type: "Obj",
            index: 58,
            element_size: 1
          }
        },
        {
          name: "SelectOptions",
          value: 47,
          union_type: {
            base_type: "Obj",
            index: 102,
            element_size: 1
          }
        },
        {
          name: "SliceOptions",
          value: 48,
          union_type: {
            base_type: "Obj",
            index: 109,
            element_size: 1
          }
        },
        {
          name: "TransposeConvOptions",
          value: 49,
          union_type: {
            base_type: "Obj",
            index: 127,
            element_size: 1
          }
        },
        {
          name: "SparseToDenseOptions",
          value: 50,
          union_type: {
            base_type: "Obj",
            index: 113,
            element_size: 1
          }
        },
        {
          name: "TileOptions",
          value: 51,
          union_type: {
            base_type: "Obj",
            index: 125,
            element_size: 1
          }
        },
        {
          name: "ExpandDimsOptions",
          value: 52,
          union_type: {
            base_type: "Obj",
            index: 36,
            element_size: 1
          }
        },
        {
          name: "EqualOptions",
          value: 53,
          union_type: {
            base_type: "Obj",
            index: 34,
            element_size: 1
          }
        },
        {
          name: "NotEqualOptions",
          value: 54,
          union_type: {
            base_type: "Obj",
            index: 75,
            element_size: 1
          }
        },
        {
          name: "ShapeOptions",
          value: 55,
          union_type: {
            base_type: "Obj",
            index: 105,
            element_size: 1
          }
        },
        {
          name: "PowOptions",
          value: 56,
          union_type: {
            base_type: "Obj",
            index: 83,
            element_size: 1
          }
        },
        {
          name: "ArgMinOptions",
          value: 57,
          union_type: {
            base_type: "Obj",
            index: 5,
            element_size: 1
          }
        },
        {
          name: "FakeQuantOptions",
          value: 58,
          union_type: {
            base_type: "Obj",
            index: 37,
            element_size: 1
          }
        },
        {
          name: "PackOptions",
          value: 59,
          union_type: {
            base_type: "Obj",
            index: 79,
            element_size: 1
          }
        },
        {
          name: "LogicalOrOptions",
          value: 60,
          union_type: {
            base_type: "Obj",
            index: 64,
            element_size: 1
          }
        },
        {
          name: "OneHotOptions",
          value: 61,
          union_type: {
            base_type: "Obj",
            index: 76,
            element_size: 1
          }
        },
        {
          name: "LogicalAndOptions",
          value: 62,
          union_type: {
            base_type: "Obj",
            index: 62,
            element_size: 1
          }
        },
        {
          name: "LogicalNotOptions",
          value: 63,
          union_type: {
            base_type: "Obj",
            index: 63,
            element_size: 1
          }
        },
        {
          name: "UnpackOptions",
          value: 64,
          union_type: {
            base_type: "Obj",
            index: 133,
            element_size: 1
          }
        },
        {
          name: "FloorDivOptions",
          value: 65,
          union_type: {
            base_type: "Obj",
            index: 39,
            element_size: 1
          }
        },
        {
          name: "SquareOptions",
          value: 66,
          union_type: {
            base_type: "Obj",
            index: 117,
            element_size: 1
          }
        },
        {
          name: "ZerosLikeOptions",
          value: 67,
          union_type: {
            base_type: "Obj",
            index: 142,
            element_size: 1
          }
        },
        {
          name: "FillOptions",
          value: 68,
          union_type: {
            base_type: "Obj",
            index: 38,
            element_size: 1
          }
        },
        {
          name: "BidirectionalSequenceLSTMOptions",
          value: 69,
          union_type: {
            base_type: "Obj",
            index: 9,
            element_size: 1
          }
        },
        {
          name: "BidirectionalSequenceRNNOptions",
          value: 70,
          union_type: {
            base_type: "Obj",
            index: 10,
            element_size: 1
          }
        },
        {
          name: "UnidirectionalSequenceLSTMOptions",
          value: 71,
          union_type: {
            base_type: "Obj",
            index: 131,
            element_size: 1
          }
        },
        {
          name: "FloorModOptions",
          value: 72,
          union_type: {
            base_type: "Obj",
            index: 40,
            element_size: 1
          }
        },
        {
          name: "RangeOptions",
          value: 73,
          union_type: {
            base_type: "Obj",
            index: 88,
            element_size: 1
          }
        },
        {
          name: "ResizeNearestNeighborOptions",
          value: 74,
          union_type: {
            base_type: "Obj",
            index: 94,
            element_size: 1
          }
        },
        {
          name: "LeakyReluOptions",
          value: 75,
          union_type: {
            base_type: "Obj",
            index: 57,
            element_size: 1
          }
        },
        {
          name: "SquaredDifferenceOptions",
          value: 76,
          union_type: {
            base_type: "Obj",
            index: 118,
            element_size: 1
          }
        },
        {
          name: "MirrorPadOptions",
          value: 77,
          union_type: {
            base_type: "Obj",
            index: 69,
            element_size: 1
          }
        },
        {
          name: "AbsOptions",
          value: 78,
          union_type: {
            base_type: "Obj",
            index: 1,
            element_size: 1
          }
        },
        {
          name: "SplitVOptions",
          value: 79,
          union_type: {
            base_type: "Obj",
            index: 116,
            element_size: 1
          }
        },
        {
          name: "UniqueOptions",
          value: 80,
          union_type: {
            base_type: "Obj",
            index: 132,
            element_size: 1
          }
        },
        {
          name: "ReverseV2Options",
          value: 81,
          union_type: {
            base_type: "Obj",
            index: 96,
            element_size: 1
          }
        },
        {
          name: "AddNOptions",
          value: 82,
          union_type: {
            base_type: "Obj",
            index: 2,
            element_size: 1
          }
        },
        {
          name: "GatherNdOptions",
          value: 83,
          union_type: {
            base_type: "Obj",
            index: 42,
            element_size: 1
          }
        },
        {
          name: "CosOptions",
          value: 84,
          union_type: {
            base_type: "Obj",
            index: 23,
            element_size: 1
          }
        },
        {
          name: "WhereOptions",
          value: 85,
          union_type: {
            base_type: "Obj",
            index: 140,
            element_size: 1
          }
        },
        {
          name: "RankOptions",
          value: 86,
          union_type: {
            base_type: "Obj",
            index: 89,
            element_size: 1
          }
        },
        {
          name: "ReverseSequenceOptions",
          value: 87,
          union_type: {
            base_type: "Obj",
            index: 95,
            element_size: 1
          }
        },
        {
          name: "MatrixDiagOptions",
          value: 88,
          union_type: {
            base_type: "Obj",
            index: 65,
            element_size: 1
          }
        },
        {
          name: "QuantizeOptions",
          value: 89,
          union_type: {
            base_type: "Obj",
            index: 85,
            element_size: 1
          }
        },
        {
          name: "MatrixSetDiagOptions",
          value: 90,
          union_type: {
            base_type: "Obj",
            index: 66,
            element_size: 1
          }
        },
        {
          name: "HardSwishOptions",
          value: 91,
          union_type: {
            base_type: "Obj",
            index: 47,
            element_size: 1
          }
        },
        {
          name: "IfOptions",
          value: 92,
          union_type: {
            base_type: "Obj",
            index: 52,
            element_size: 1
          }
        },
        {
          name: "WhileOptions",
          value: 93,
          union_type: {
            base_type: "Obj",
            index: 141,
            element_size: 1
          }
        },
        {
          name: "DepthToSpaceOptions",
          value: 94,
          union_type: {
            base_type: "Obj",
            index: 27,
            element_size: 1
          }
        },
        {
          name: "NonMaxSuppressionV4Options",
          value: 95,
          union_type: {
            base_type: "Obj",
            index: 73,
            element_size: 1
          }
        },
        {
          name: "NonMaxSuppressionV5Options",
          value: 96,
          union_type: {
            base_type: "Obj",
            index: 74,
            element_size: 1
          }
        },
        {
          name: "ScatterNdOptions",
          value: 97,
          union_type: {
            base_type: "Obj",
            index: 100,
            element_size: 1
          }
        },
        {
          name: "SelectV2Options",
          value: 98,
          union_type: {
            base_type: "Obj",
            index: 103,
            element_size: 1
          }
        },
        {
          name: "DensifyOptions",
          value: 99,
          union_type: {
            base_type: "Obj",
            index: 26,
            element_size: 1
          }
        },
        {
          name: "SegmentSumOptions",
          value: 100,
          union_type: {
            base_type: "Obj",
            index: 101,
            element_size: 1
          }
        },
        {
          name: "BatchMatMulOptions",
          value: 101,
          union_type: {
            base_type: "Obj",
            index: 7,
            element_size: 1
          }
        },
        {
          name: "CumsumOptions",
          value: 102,
          union_type: {
            base_type: "Obj",
            index: 24,
            element_size: 1
          }
        },
        {
          name: "CallOnceOptions",
          value: 103,
          union_type: {
            base_type: "Obj",
            index: 16,
            element_size: 1
          }
        },
        {
          name: "BroadcastToOptions",
          value: 104,
          union_type: {
            base_type: "Obj",
            index: 13,
            element_size: 1
          }
        },
        {
          name: "Rfft2dOptions",
          value: 105,
          union_type: {
            base_type: "Obj",
            index: 97,
            element_size: 1
          }
        },
        {
          name: "Conv3DOptions",
          value: 106,
          union_type: {
            base_type: "Obj",
            index: 22,
            element_size: 1
          }
        },
        {
          name: "HashtableOptions",
          value: 107,
          union_type: {
            base_type: "Obj",
            index: 50,
            element_size: 1
          }
        },
        {
          name: "HashtableFindOptions",
          value: 108,
          union_type: {
            base_type: "Obj",
            index: 48,
            element_size: 1
          }
        },
        {
          name: "HashtableImportOptions",
          value: 109,
          union_type: {
            base_type: "Obj",
            index: 49,
            element_size: 1
          }
        },
        {
          name: "HashtableSizeOptions",
          value: 110,
          union_type: {
            base_type: "Obj",
            index: 51,
            element_size: 1
          }
        },
        {
          name: "VarHandleOptions",
          value: 111,
          union_type: {
            base_type: "Obj",
            index: 138,
            element_size: 1
          }
        },
        {
          name: "ReadVariableOptions",
          value: 112,
          union_type: {
            base_type: "Obj",
            index: 90,
            element_size: 1
          }
        },
        {
          name: "AssignVariableOptions",
          value: 113,
          union_type: {
            base_type: "Obj",
            index: 6,
            element_size: 1
          }
        },
        {
          name: "RandomOptions",
          value: 114,
          union_type: {
            base_type: "Obj",
            index: 87,
            element_size: 1
          }
        },
        {
          name: "BucketizeOptions",
          value: 115,
          union_type: {
            base_type: "Obj",
            index: 14,
            element_size: 1
          }
        },
        {
          name: "GeluOptions",
          value: 116,
          union_type: {
            base_type: "Obj",
            index: 44,
            element_size: 1
          }
        },
        {
          name: "DynamicUpdateSliceOptions",
          value: 117,
          union_type: {
            base_type: "Obj",
            index: 32,
            element_size: 1
          }
        },
        {
          name: "UnsortedSegmentProdOptions",
          value: 118,
          union_type: {
            base_type: "Obj",
            index: 136,
            element_size: 1
          }
        },
        {
          name: "UnsortedSegmentMaxOptions",
          value: 119,
          union_type: {
            base_type: "Obj",
            index: 134,
            element_size: 1
          }
        },
        {
          name: "UnsortedSegmentMinOptions",
          value: 120,
          union_type: {
            base_type: "Obj",
            index: 135,
            element_size: 1
          }
        },
        {
          name: "UnsortedSegmentSumOptions",
          value: 121,
          union_type: {
            base_type: "Obj",
            index: 137,
            element_size: 1
          }
        },
        {
          name: "ATan2Options",
          value: 122,
          union_type: {
            base_type: "Obj",
            index: 0,
            element_size: 1
          }
        },
        {
          name: "SignOptions",
          value: 123,
          union_type: {
            base_type: "Obj",
            index: 106,
            element_size: 1
          }
        },
        {
          name: "BitcastOptions",
          value: 124,
          union_type: {
            base_type: "Obj",
            index: 11,
            element_size: 1
          }
        },
        {
          name: "BitwiseXorOptions",
          value: 125,
          union_type: {
            base_type: "Obj",
            index: 12,
            element_size: 1
          }
        },
        {
          name: "RightShiftOptions",
          value: 126,
          union_type: {
            base_type: "Obj",
            index: 98,
            element_size: 1
          }
        }
      ],
      is_union: true,
      underlying_type: {
        base_type: "UType",
        index: 2,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.CombinerType",
      values: [
        {
          name: "SUM",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "MEAN",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SQRTN",
          value: 2,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 3,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.CustomOptionsFormat",
      values: [
        {
          name: "FLEXBUFFERS",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 4,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.DimensionType",
      values: [
        {
          name: "DENSE",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPARSE_CSR",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 5,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.FullyConnectedOptionsWeightsFormat",
      values: [
        {
          name: "DEFAULT",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SHUFFLED4x16INT8",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 6,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.LSHProjectionType",
      values: [
        {
          name: "UNKNOWN",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SPARSE",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "DENSE",
          value: 2,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 7,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.LSTMKernelType",
      values: [
        {
          name: "FULL",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BASIC",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 8,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.MirrorPadMode",
      values: [
        {
          name: "REFLECT",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "SYMMETRIC",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 9,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.Padding",
      values: [
        {
          name: "SAME",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "VALID",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 10,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.QuantizationDetails",
      values: [
        {
          name: "NONE",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "CustomQuantization",
          value: 1,
          union_type: {
            base_type: "Obj",
            index: 25,
            element_size: 1
          }
        }
      ],
      is_union: true,
      underlying_type: {
        base_type: "UType",
        index: 11,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.SparseIndexVector",
      values: [
        {
          name: "NONE",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "Int32Vector",
          value: 1,
          union_type: {
            base_type: "Obj",
            index: 53,
            element_size: 1
          }
        },
        {
          name: "Uint16Vector",
          value: 2,
          union_type: {
            base_type: "Obj",
            index: 129,
            element_size: 1
          }
        },
        {
          name: "Uint8Vector",
          value: 3,
          union_type: {
            base_type: "Obj",
            index: 130,
            element_size: 1
          }
        }
      ],
      is_union: true,
      underlying_type: {
        base_type: "UType",
        index: 12,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    },
    {
      name: "tflite.TensorType",
      values: [
        {
          name: "FLOAT32",
          value: 0,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FLOAT16",
          value: 1,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "INT32",
          value: 2,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UINT8",
          value: 3,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "INT64",
          value: 4,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "STRING",
          value: 5,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "BOOL",
          value: 6,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "INT16",
          value: 7,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "COMPLEX64",
          value: 8,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "INT8",
          value: 9,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "FLOAT64",
          value: 10,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "COMPLEX128",
          value: 11,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UINT64",
          value: 12,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "RESOURCE",
          value: 13,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "VARIANT",
          value: 14,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UINT32",
          value: 15,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "UINT16",
          value: 16,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        },
        {
          name: "INT4",
          value: 17,
          union_type: {
            base_size: 1,
            element_size: 1
          }
        }
      ],
      underlying_type: {
        base_type: "Byte",
        index: 13,
        base_size: 1,
        element_size: 1
      },
      declaration_file: ""
    }
  ],
  file_ident: "TFL3",
  file_ext: "tflite",
  root_table: {
    name: "tflite.Model",
    fields: [
      {
        name: "buffers",
        type: {
          base_type: "Vector",
          element: "Obj",
          index: 15,
          element_size: 4
        },
        id: 4,
        offset: 12,
        optional: true
      },
      {
        name: "description",
        type: {
          base_type: "String",
          element_size: 1
        },
        id: 3,
        offset: 10,
        optional: true
      },
      {
        name: "metadata",
        type: {
          base_type: "Vector",
          element: "Obj",
          index: 68,
          element_size: 4
        },
        id: 6,
        offset: 16,
        optional: true
      },
      {
        name: "metadata_buffer",
        type: {
          base_type: "Vector",
          element: "Int",
          element_size: 4
        },
        id: 5,
        offset: 14,
        optional: true
      },
      {
        name: "operator_codes",
        type: {
          base_type: "Vector",
          element: "Obj",
          index: 78,
          element_size: 4
        },
        id: 1,
        offset: 6,
        optional: true
      },
      {
        name: "signature_defs",
        type: {
          base_type: "Vector",
          element: "Obj",
          index: 107,
          element_size: 4
        },
        id: 7,
        offset: 18,
        optional: true
      },
      {
        name: "subgraphs",
        type: {
          base_type: "Vector",
          element: "Obj",
          index: 121,
          element_size: 4
        },
        id: 2,
        offset: 8,
        optional: true
      },
      {
        name: "version",
        type: {
          base_type: "UInt",
          element_size: 1
        },
        offset: 4
      }
    ],
    minalign: 1,
    declaration_file: ""
  },
  services: [

  ]
}))
