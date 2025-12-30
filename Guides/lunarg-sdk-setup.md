# Lunarg Vulkan SDK Setup
The following steps are intended for setting up the linux tarball version, to be performed after download.

upgrade system
```
sudo dnf update
```

install xz
```
sudo dnf install xz
```

install dependencies
```
sudo dnf install @development-tools glm-devel cmake libpng-devel wayland-devel \
libpciaccess-devel libX11-devel libXpresent libxcb xcb-util libxcb-devel libXrandr-devel \
xcb-util-keysyms-devel xcb-util-wm-devel python3 git lz4-devel libzstd-devel python3-distutils-extra qt \
gcc-g++ wayland-protocols-devel ninja-build python3-jsonschema qt5-qtbase-devel qt6-qtbase-devel
```

Download, then extract. Usually I move this to my home directory afterwards.
```
tar xf $HOME/Downloads/vulkansdk-linux-x86_64-1.x.yy.z.tar.xz
```

Runtime dependencies
```
sudo dnf install xinput libXinerama xcb-util-cursor
```

Build everything, using the maximum number of threads
```
./vulkansdk --maxjobs
```

in bashrc: export vulkan variables. Putting this in bashrc ensures they are permanently set.

```
source $HOME/vulkan/1.x.yy.z/setup-env.sh
```
Finally copy relevant files to the system!

vulkan header files
```
sudo cp -r $VULKAN_SDK/include/vulkan/ /usr/local/include/
```

vulkan loader files
```
sudo cp -P $VULKAN_SDK/lib/libvulkan.so* /usr/local/lib/
```

vulkan layer files
```
sudo cp $VULKAN_SDK/lib/libVkLayer_*.so /usr/local/lib/
sudo mkdir -p /usr/local/share/vulkan/explicit_layer.d
sudo cp $VULKAN_SDK/share/vulkan/explicit_layer.d/VkLayer_*.json /usr/local/share/vulkan/explicit_layer.d
```