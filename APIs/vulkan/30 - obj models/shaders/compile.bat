set spirvCompiler=C:\VulkanSDK\1.4.304.1\Bin\glslc.exe
set compilerFlags=--target-env=vulkan1.3

for %%f in (*.comp) do %spirvCompiler% %%~nf.comp -o %%~nf.spv %compilerFlags%