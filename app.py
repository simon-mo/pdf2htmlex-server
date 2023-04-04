import asyncio
import shlex
import shutil
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Response, UploadFile
from pydantic import BaseModel, Field

app = FastAPI()


class PDFtoHTMLOptions(BaseModel):
    """Options for the pdf2htmlEX command

    Usage: pdf2htmlEX [options] <input.pdf> [<output.html>]
    -f,--first-page <int>         first page to convert (default: 1)
    -l,--last-page <int>          last page to convert (default: 2147483647)
    --zoom <fp>                   zoom ratio
    --fit-width <fp>              fit width to <fp> pixels
    --fit-height <fp>             fit height to <fp> pixels
    --use-cropbox <int>           use CropBox instead of MediaBox (default: 1)
    --dpi <fp>                    Resolution for graphics in DPI (default: 144)
    --embed <string>              specify which elements should be embedded into output
    --embed-css <int>             embed CSS files into output (default: 1)
    --embed-font <int>            embed font files into output (default: 1)
    --embed-image <int>           embed image files into output (default: 1)
    --embed-javascript <int>      embed JavaScript files into output (default: 1)
    --embed-outline <int>         embed outlines into output (default: 1)
    --split-pages <int>           split pages into separate files (default: 0)
    --dest-dir <string>           specify destination directory (default: ".")
    --css-filename <string>       filename of the generated css file (default: "")
    --page-filename <string>      filename template for split pages  (default: "")
    --outline-filename <string>   filename of the generated outline file (default: "")
    --process-nontext <int>       render graphics in addition to text (default: 1)
    --process-outline <int>       show outline in HTML (default: 1)
    --process-annotation <int>    show annotation in HTML (default: 0)
    --process-form <int>          include text fields and radio buttons (default: 0)
    --printing <int>              enable printing support (default: 1)
    --fallback <int>              output in fallback mode (default: 0)
    --tmp-file-size-limit <int>   Maximum size (in KB) used by temporary files, -1 for no limit (default: -1)
    --embed-external-font <int>   embed local match for external fonts (default: 1)
    --font-format <string>        suffix for embedded font files (ttf,otf,woff,svg) (default: "woff")
    --decompose-ligature <int>    decompose ligatures, such as ﬁ -> fi (default: 0)
    --turn-off-ligatures <int>    explicitly tell browsers not to use ligatures (default: 0)
    --auto-hint <int>             use fontforge autohint on fonts without hints (default: 0)
    --external-hint-tool <string> external tool for hinting fonts (overrides --auto-hint) (default: "")
    --stretch-narrow-glyph <int>  stretch narrow glyphs instead of padding them (default: 0)
    --squeeze-wide-glyph <int>    shrink wide glyphs instead of truncating them (default: 1)
    --override-fstype <int>       clear the fstype bits in TTF/OTF fonts (default: 0)
    --process-type3 <int>         convert Type 3 fonts for web (experimental) (default: 0)
    --heps <fp>                   horizontal threshold for merging text, in pixels (default: 1)
    --veps <fp>                   vertical threshold for merging text, in pixels (default: 1)
    --space-threshold <fp>        word break threshold (threshold * em) (default: 0.125)
    --font-size-multiplier <fp>   a value greater than 1 increases the rendering accuracy (default: 4)
    --space-as-offset <int>       treat space characters as offsets (default: 0)
    --tounicode <int>             how to handle ToUnicode CMaps (0=auto, 1=force, -1=ignore) (default: 0)
    --optimize-text <int>         try to reduce the number of HTML elements used for text (default: 0)
    --correct-text-visibility <int> 0: Don't do text visibility checks. 1: Fully occluded text handled. 2: Partially occluded text handled (default: 1)
    --covered-text-dpi <fp>       Rendering DPI to use if correct-text-visibility == 2 and there is partially covered text on the page (default: 300)
    --bg-format <string>          specify background image format (default: "png")
    --svg-node-count-limit <int>  if node count in a svg background image exceeds this limit, fall back this page to bitmap background; negative value means no limit (default: -1)
    --svg-embed-bitmap <int>      1: embed bitmaps in svg background; 0: dump bitmaps to external files if possible (default: 1)
    -o,--owner-password <string>  owner password (for encrypted files)
    -u,--user-password <string>   user password (for encrypted files)
    --no-drm <int>                override document DRM settings (default: 0)
    --clean-tmp <int>             remove temporary files after conversion (default: 1)
    --tmp-dir <string>            specify the location of temporary directory (default: "/tmp")
    --data-dir <string>           specify data directory (default: "/usr/local/share/pdf2htmlEX")
    --poppler-data-dir <string>   specify poppler data directory (default: "/usr/local/share/pdf2htmlEX/poppler")
    --debug <int>                 print debugging information (default: 0)
    --proof <int>                 texts are drawn on both text layer and background for proof (default: 0)
    --quiet <int>                 perform operations quietly (default: 0)
    -v,--version                  print copyright and version info
    -h,--help                     print usage information
    """

    first_page: int = Field(1, description="first page to convert")
    last_page: int = Field(2147483647, description="last page to convert")
    zoom: float = Field(None, description="zoom ratio")
    fit_width: float = Field(None, description="fit width to <fp> pixels")
    fit_height: float = Field(None, description="fit height to <fp> pixels")
    use_cropbox: bool = Field(True, description="use CropBox instead of MediaBox")
    dpi: float = Field(144, description="Resolution for graphics in DPI")
    embed: str = Field(None, description="specify which elements should be embedded into output")
    embed_css: bool = Field(True, description="embed CSS files into output")
    embed_font: bool = Field(True, description="embed font files into output")
    embed_image: bool = Field(True, description="embed image files into output")
    embed_javascript: bool = Field(True, description="embed JavaScript files into output")
    embed_outline: bool = Field(True, description="embed outlines into output")
    split_pages: bool = Field(False, description="split pages into separate files")
    dest_dir: str = Field(".", description="specify destination directory")
    css_filename: str = Field(None, description="filename of the generated css file")
    page_filename: str = Field(None, description="filename template for split pages")
    outline_filename: str = Field(None, description="filename of the generated outline file")
    process_nontext: bool = Field(True, description="render graphics in addition to text")
    process_outline: bool = Field(True, description="show outline in HTML")
    process_annotation: bool = Field(False, description="show annotation in HTML")
    process_form: bool = Field(False, description="include text fields and radio buttons")
    printing: bool = Field(True, description="enable printing support")
    fallback: bool = Field(False, description="output in fallback mode")
    tmp_file_size_limit: int = Field(-1, description="Maximum size (in KB) used by temporary files, -1 for no limit")
    embed_external_font: bool = Field(True, description="embed local match for external fonts")
    font_format: str = Field("woff", description="suffix for embedded font files (ttf,otf,woff,svg)")
    decompose_ligature: bool = Field(False, description="decompose ligatures, such as ﬁ -> fi")
    turn_off_ligatures: bool = Field(False, description="explicitly tell browsers not to use ligatures")
    auto_hint: bool = Field(False, description="use fontforge autohint on fonts without hints")
    external_hint_tool: str = Field(None, description="external tool for hinting fonts (overrides --auto-hint)")
    stretch_narrow_glyph: bool = Field(False, description="stretch narrow glyphs instead of padding them")
    squeeze_wide_glyph: bool = Field(True, description="shrink wide glyphs instead of truncating them")
    override_fstype: bool = Field(False, description="clear the fstype bits in TTF/OTF fonts")
    process_type3: bool = Field(False, description="convert Type 3 fonts for web (experimental)")
    heps: float = Field(1, description="horizontal threshold for merging text, in pixels")
    veps: float = Field(1, description="vertical threshold for merging text, in pixels")
    space_threshold: float = Field(0.125, description="word break threshold (threshold * em)")
    font_size_multiplier: float = Field(4, description="a value greater than 1 increases the rendering accuracy")
    space_as_offset: bool = Field(False, description="treat space characters as offsets")
    tounicode: int = Field(0, description="how to handle ToUnicode CMaps (0=auto, 1=force, -1=ignore)")
    optimize_text: bool = Field(False, description="try to reduce the number of HTML elements used for text")
    correct_text_visibility: int = Field(
        1, description="0: Don't do text visibility checks. 1: Fully occluded text handled. 2: Partially occluded text handled"
    )
    covered_text_dpi: float = Field(
        300, description="Rendering DPI to use if correct-text-visibility == 2 and there is partially covered text on the page"
    )
    bg_format: str = Field("png", description="specify background image format")
    svg_node_count_limit: int = Field(
        -1,
        description="if node count in a svg background image exceeds this limit, fall back this page to bitmap background; negative value means no limit",
    )
    svg_embed_bitmap: int = Field(1, description="1: embed bitmaps in svg background; 0: dump bitmaps to external files if possible")
    owner_password: str = Field(None, description="owner password (for encrypted files)")
    user_password: str = Field(None, description="user password (for encrypted files)")
    no_drm: int = Field(0, description="override document DRM settings")
    clean_tmp: int = Field(1, description="remove temporary files after conversion")
    tmp_dir: str = Field("/tmp", description="specify the location of temporary directory")
    data_dir: str = Field("/usr/local/share/pdf2htmlEX", description="specify data directory")
    poppler_data_dir: str = Field("/usr/local/share/pdf2htmlEX/poppler", description="specify poppler data directory")
    debug: int = Field(0, description="print debugging information")
    proof: int = Field(0, description="texts are drawn on both text layer and background for proof")
    quiet: int = Field(0, description="perform operations quietly")
    version: bool = Field(False, description="print copyright and version info")
    help: bool = Field(False, description="print usage information")


@app.post("/docs", description="This endpoint returns the documentation for the pdf2html endpoint")
def doc(options: PDFtoHTMLOptions):
    return options


@app.post("/pdf2html", description="This endpoint converts a pdf file to html")
async def pdf2html(
    cli_extra_args: str = "",
    file_upload: UploadFile = File(...),
):
    with NamedTemporaryFile(delete=False) as inp_file:
        shutil.copyfileobj(file_upload.file, inp_file)
        inp_file.flush()

        out_file_path = inp_file.name + ".html"

        cmdline = shlex.split(f"pdf2htmlEX {inp_file.name} {out_file_path} --dest-dir=/ {cli_extra_args}")
        print(cmdline)
        proc = await asyncio.subprocess.create_subprocess_exec(*cmdline)
        await proc.wait()

        with open(out_file_path, "rb") as f:
            return Response(f.read(), media_type="text/html")
