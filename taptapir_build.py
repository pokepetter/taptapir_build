import sys
from pathlib import Path
import re
import base64
import shutil
import subprocess
import time
import textwrap


def build(source_code, name, taptapir_folder='../taptapir/'):
    # print(source_code)
    if source_code.strip() == '':
        raise Exception('no source code found')



    # print(combined_sunsnake_code)

    # pattern = r"texture\s*=\s*'(.*?)'"
    # texture_names = re.findall(pattern, combined_sunsnake_code)
    #
    # textures_as_base_64_strings = dict()
    # [print(i, e) for i, e in enumerate(texture_names)]
    # for name in texture_names:
    #     suffix = 'png'
    #     if '.' in name:
    #         suffix = name.split('.')[1]
    #
    #     with open(name, "rb") as image_file:
    #         textures_as_base_64_strings[name] = f'data:image/{suffix};base64,' + base64.b64encode(image_file.read()).decode('utf-8')
    #
    # # for name in texture_names:
    # #     combined_sunsnake_code = combined_sunsnake_code.replace(f"texture='{name}'", f"texture=TAPTAPIR_TEXTURES['{name}']")
    #
    # textures_as_base_64_strings = '{' + '\n\n'.join(f"'{key}' : '{value}', " for key, value in textures_as_base_64_strings.items()) + '\n}'
    # combined_sunsnake_code = f'TAPTAPIR_TEXTURES = {textures_as_base_64_strings}\n {combined_sunsnake_code}'
    # print(combined_sunsnake_code)

    # package_folder = Path(__file__).parent
    taptapir_folder = Path(taptapir_folder).resolve()

    with open(taptapir_folder/'taptapir.js', 'r') as f:
        taptapir_source = f.read()

    with open(taptapir_folder/'sunsnake_compiler.js', 'r') as f:
        sunsnake_compiler_source = f.read()

    output_folder = Path('builds')
    output_folder.mkdir(parents=True, exist_ok=True)
    out_path = output_folder / f'{name}_build.html'
    title = name.replace('_',' ').title()
    html_content = (f'''\
<html>
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<title>{title}</title>
</head><body></body>
<script type='text/javascript'>
{taptapir_source}
</script>

<script type='text/sunsnake'>
{source_code}
</script>

<script type='text/javascript'>
{sunsnake_compiler_source}
</script>
</html>
    ''')

    with out_path.open('w') as out_file:
        out_file.write(html_content)
    print('compiled to:', out_path)

    icon_path = Path('.') / 'icon.png'
    if not icon_path.exists():
        icon_path = Path(__file__ / 'icon.png')

    shutil.copy(icon_path, 'builds/icon.png')
    return html_content


if __name__ == '__main__':
    print('running taptapir_build:', sys.argv)
    if len(sys.argv) <= 1:
        build_test_project = input("no html file provided, build test project? [y,N]: ").strip().lower() == 'y'
        if not build_test_project:
            raise Exception('Please specify target .html file to build')

        import textwrap
        all_html_code = textwrap.dedent('''\
            set_window_color('rgb(49 72 60)')
            b = Button(scale=[.6,.2], text='test build :D', color=color.azure, shadow=True, text_color=color.white)
            b.on_click = def():
                b.color = color.random_color()
            Entity(scale=[.3,.2], texture='icon.png', y=.3, roundness=.1)
            ''')
        name = 'test_build'

    else:
        source_file_path = Path(sys.argv[1]).resolve()
        print('Building file:', source_file_path)
        name = source_file_path.stem
        with source_file_path.open('r') as source_file:
            all_html_code = source_file.read()
            if not all_html_code:
                raise Exception(f'Error: File is empty: {source_file}')


    delimiter = "<script type='text/sunsnake'>"
    if delimiter not in all_html_code:
        print('code is not using html, so no need to extract sunsnake code')
        combined_sunsnake_code = all_html_code
    else:
        sunsnake_code_blocks = (delimiter + all_html_code.split(delimiter, 1)[1]).split(delimiter)
        combined_sunsnake_code = ''
        for part in sunsnake_code_blocks:
            combined_sunsnake_code += part.split("</script>")[0]
        # print('sunsnake code:\n', combined_sunsnake_code)

    print('building html...')
    t = time.time()
    html_content = build(combined_sunsnake_code, name=name)
    print('built html in:', time.time() - t)

    build_for_android = '--android' in sys.argv
    # build_for_android = True

    if build_for_android:
        'making android build...'
        from taptapir_build_android import generate_webview_android_app
        icon_path = Path('.') / 'icon.png'
        if not icon_path.exists():
            icon_path = Path(__file__ / 'icon.png')

        package_name = "com.mydomain.mycoolapp"
        version = 0
        banner_bottom_ad_unit_id = None

        for arg in sys.argv:
            if arg.startswith('banner_bottom_ad_unit_id='):
                banner_bottom_ad_unit_id = arg[len('banner_bottom_ad_unit_id='):]
            if arg.startswith('package_name='):
                package_name = arg[len('package_name='):]
            if arg.startswith('version='):
                version = int(arg[len('version='):])

        include_admob = '--include_admob' in sys.argv
        release = '--release' in sys.argv

        generate_webview_android_app(
            app_name=name,
            version=version,
            package_name=package_name,
            html_content=html_content,
            icon_path=icon_path.resolve(),
            include_admob=include_admob,
            banner_bottom_ad_unit_id=banner_bottom_ad_unit_id,
            project_dir=f"builds/{name}_android",
            release=release,
        )

        # run_in_emulator = input("Run in emulator? [y,N]: ").strip().lower() == 'y'
        run_in_emulator = '--run_in_emulator' in sys.argv
        if run_in_emulator:
            print('current path:', Path('.').resolve())
            if not release:
                apk_path = (Path('.') / f"builds/{name}_android/app/build/outputs/apk/debug/app-debug.apk").resolve()
            else:
                apk_path = (Path('.') / f"builds/{name}_android/app/build/outputs/bundle/release/app-release.aab").resolve()

            if not apk_path.exists():
                raise Exception('apk not found at:', apk_path)


            # Step 1: Start the emulator in a separate process
            emulator_name = "MyEmulator"
            print(f"Starting emulator: {emulator_name}")
            emulator_process = subprocess.Popen(
                ["emulator", "-avd", emulator_name, '-no-audio'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Step 2: Wait until the emulator is fully booted
            print("Waiting for emulator to boot...")
            subprocess.run(["adb", "wait-for-device"], check=True)

            booted = False
            while not booted:
                output = subprocess.check_output(
                    ["adb", "shell", "getprop", "sys.boot_completed"],
                    encoding="utf-8"
                ).strip()
                if output == "1":
                    booted = True
                else:
                    time.sleep(2)

            print("Emulator booted!")

            # Step 3: Install the app
            print(f"Installing APK: {apk_path}")
            subprocess.run(["adb", "install", "-r", apk_path], check=True)

            # Step 4: Start the app
            main_activity = ".MainActivity"
            print(f"Starting app: {package_name}{main_activity}")
            subprocess.run(
                ["adb", "shell", "am", "start", "-n", f"{package_name}/{main_activity}"],
                check=True
            )

            # Step 5: Optionally keep emulator running
            keep_emulator_running = input("Keep emulator running? [y,N]: ").strip().lower() == 'y'
            if not keep_emulator_running:
                print("Shutting down emulator...")
                subprocess.run(["adb", "emu", "kill"])
                emulator_process.terminate()
            else:
                subprocess.run(f"adb logcat -c", shell=True, check=True) # clear
                subprocess.run(
                    # f"adb logcat *:E | grep {package_name}", shell=True, check=True)
                    f"adb logcat *:E", shell=True, check=True)
