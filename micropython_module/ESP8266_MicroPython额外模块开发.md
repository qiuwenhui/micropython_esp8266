# ESP8266_MicroPython额外模块开发

## 参考

### micropython 文档

官方文档：<http://docs.micropython.org/en/latest/>

### micropython 新硬件开发文档参考

<https://github.com/micropython/micropython/wiki/Hardware-API>

<https://github.com/micropython/micropython/issues/1430>

### MicroPython 模块 开发论坛



### ESP8266  esp-open-sdk

<https://github.com/pfalcon/esp-open-sdk

安装部署后 包含 SDK和工具链,已经整合到工具链中

#### Esp8266 _NONOS_SDK

版本：Esp8266 _NONOS_sdk-2.1.0-18

<https://bbs.espressif.com/viewforum.php?f=46>

SDK Development Guide @ http://bbs.espressif.com/viewtopic.php?f=51&t=1023
All documentations @ http://bbs.espressif.com/viewforum.php?f=51

#### 官方文档

<https://www.espressif.com/zh-hans/products/hardware/esp8266ex/resources>

### ESP8266 官网

<https://www.espressif.com/zh-hans/products/hardware/esp8266ex/overview>

### ESP8266 SDK 论坛

<https://bbs.espressif.com/index.php>

## MicroPython 模块 开发

官方参考文档

<http://docs.micropython.org/en/latest/develop/cmodules.html>

### 安装部署SDK和工具链

esp-open-sdk

参考《Esp8266 安装和部署》

## 开发构建MicroPython模块

### MicroPython外部C模块

#### 外部C模块的结构

在开发用于MicroPython的模块时，您可能会发现自己遇到了Python环境的限制，通常是由于无法访问某些硬件资源或Python速度限制。

如果无法通过[最大化MicroPython Speed中的](http://docs.micropython.org/en/latest/reference/speed_python.html#speed-python)建议来解决您的限制，则在C中编写部分或全部模块是可行的选择。

<font size="3" color="yellow">本章介绍如何将此类外部模块编译为**MicroPython可执行文件或固件映像。</font>

MicroPython用户C模块是包含以下文件的目录：

- `*.c`和/或`*.h`模块的源代码文件。

  这些通常包括正在实现的低级功能和用于公开功能和模块的MicroPython绑定功能。

  目前，编写这些函数/模块的最佳参考是在MicroPython树中查找类似的模块并将它们用作示例。

- `micropython.mk` 包含此模块的Makefile片段。

  `$(USERMOD_DIR)`可用作`micropython.mk`模块目录的路径。因为它是为每个c模块重新定义的，所以应该在你`micropython.mk`的本地make变量中进行扩展，例如`EXAMPLE_MOD_DIR := $(USERMOD_DIR)`

  你`micropython.mk`必须添加你的控制模块C相对于你扩大复制文件`$(USERMOD_DIR)`到`SRC_USERMOD`，如`SRC_USERMOD += $(EXAMPLE_MOD_DIR)/example.c`

  如果您有自定义`CFLAGS`设置或包含要定义的文件夹，则应将这些设置添加到`CFLAGS_USERMOD`。

##### 基本范例

> 这个名为simple的模块`example`提供了一个函数 ，它将两个整数args加在一起并返回结果。`example.add_ints(a, b)`

```shell
example/
├── example.c
└── micropython.mk
```

<font color="yellow" >example.c</font>

```c
// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

// This is the function which will be called from Python as example.add_ints(a, b).
STATIC mp_obj_t example_add_ints(mp_obj_t a_obj, mp_obj_t b_obj) {
    // Extract the ints from the micropython input objects
    int a = mp_obj_get_int(a_obj);
    int b = mp_obj_get_int(b_obj);

    // Calculate the addition and convert to MicroPython object.
    return mp_obj_new_int(a + b);
}
// Define a Python reference to the function above
STATIC MP_DEFINE_CONST_FUN_OBJ_2(example_add_ints_obj, example_add_ints);

// Define all properties of the example module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },
    { MP_ROM_QSTR(MP_QSTR_add_ints), MP_ROM_PTR(&example_add_ints_obj) },
};
STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);

// Define module object.
const mp_obj_module_t example_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&example_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_example, example_user_cmodule, MODULE_EXAMPLE_ENABLED);
```

<font color="yellow" >micropython.mk</font>

```makefile
EXAMPLE_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(EXAMPLE_MOD_DIR)/example.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(EXAMPLE_MOD_DIR)
```

最后，您需要修改<font color="red" >mpconfigboard.h </font>您的电路板，通过添加以下内容来告诉构建过程包含新模块

```c
#define MODULE_EXAMPLE_ENABLED（1）
```

##### 编译cmodule到MicroPython

要构建这样的模块，请使用额外的<font color="red" >`make`</font>标签名<font color="red">USER_C_MODULES </font> 设置包含的所有模块的目录（而不是模块本身）,编译MicroPython（请参阅[入门](https://github.com/micropython/micropython/wiki/Getting-Started)）。

目录：

```shell
my_project/
├── modules/
│   └──example/
│       ├──example.c
│       └──micropython.mk
└── micropython/
    ├──ports/
   ... ├──stm32/
      ...
```

Building for stm32 port:

```shell
cd my_project/micropython/ports/esp8266
make USER_C_MODULES=../../../modules all
```

##### MicroPython中的模块用法

一旦内置到您的MicroPython副本中，`example.c`现在可以在Python中访问上面实现的模块，就像任何其他内置模块一样，例如

```python
import example
print(example.add_ints(1, 3))
# should display 4
```