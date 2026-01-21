import re
import asyncio
import asyncio
import argparse
import typing as t

from fastapi import (
    FastAPI,
    Request,
    Response,
    HTTPException,
    Query,
)

from fastapi.responses import (
    StreamingResponse,
)

import gitproto

ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9-_]+$")

app = FastAPI()


@app.get("/")
def get_index():
    raise HTTPException(401)


@app.head("/")
def head_index():
    raise HTTPException(401)


@app.get("/{user}/{repo}/info/refs")
async def get_repo_info_refs(user: str, repo: str, service: t.Annotated[str, Query()]):
    # could do something funny here and serve specific films based on repo selection
    if not ALPHANUMERIC_PATTERN.match(user) or not ALPHANUMERIC_PATTERN.match(repo):
        raise HTTPException(
            status_code=401,
            detail="Parameters must be alphanumeric without special characters.",
        )

    return Response(
        status_code=200,
        headers={
            "Content-Type": "application/x-git-upload-pack-advertisement",
        },
        content=gitproto.create_advertisement(),
    )


@app.get("/{user}/{repo}/HEAD")
async def get_repo_head():
    return Response(
        status_code=401,
        content="",
        headers={"WWW-Authenticate": 'Basic realm=""'},
    )


@app.post("/{user}/{repo}/git-upload-pack")
async def process_upload_pack_req(req: Request):
    req_body = await req.body()
    decoded = gitproto.decode_buffer(req_body)
    command = decoded[0].split(b"=")[1]

    match command:
        case b"ls-refs\n":
            return Response(
                status_code=200,
                content=gitproto.create_ref_list(),
                headers={
                    "Content-Type": "application/x-git-upload-pack-result",
                },
            )

        case b"fetch":
            return StreamingResponse(
                player.stream(), media_type="application/x-git-upload-pack-result"
            )

        case _:
            print(f'unknown command "{command}"')
            return Response(status_code=500)


class GitemaPlayer:
    def __init__(self, film_path: str, speed: float = 1 / 30, replay: bool = False):
        self.speed = speed
        self.frames = []
        self.replay = replay

        with open(film_path, "r") as file:
            data = file.read()
            self.frames = data.split("EOF\n")[:-1]

    async def stream(self):
        buffer = b""
        buffer += gitproto.write_pktline("packfile\n")
        yield buffer

        last_frame_height = 0
        last_frame_width = 0

        while True:
            for frame in self.frames:
                f = frame.split("\n")
                last_frame_height = len(f) - 1
                last_frame_width = max(len(row) for row in f)

                yield gitproto.write_pktline(
                    gitproto.write_message(
                        gitproto.SidebandChannel.Progress, f"{str(frame)}"
                    )
                )
                yield gitproto.write_pktline(
                    gitproto.write_message(
                        gitproto.SidebandChannel.Progress,
                        f"\r\x1b[{last_frame_height}A",
                    )
                )
                await asyncio.sleep(self.speed)

            if not self.replay:
                break

        final = "\n".join("" * last_frame_width for _ in range(last_frame_height))
        yield gitproto.write_pktline(
            gitproto.write_message(gitproto.SidebandChannel.Progress, final + "\n")
        )
        yield gitproto.write_pktline(
            gitproto.write_message(gitproto.SidebandChannel.Error, "bye bye!\n"),
        )


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("film")
    parser.add_argument("-p", "--playback-speed", type=float, default=1 / 30)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--replay", action="store_true")

    args = parser.parse_args()
    player = GitemaPlayer(args.film, args.playback_speed, replay=args.replay)

    uvicorn.run(app, host=args.host, port=args.port)
