.PHONY: all test test-vision test-controller test-dashboard build clean

all: test build

# === Tests ===
test: test-vision test-controller

test-vision:
cd vision_pipeline && python -m pytest tests/ -v --tb=short

test-controller:
cd tracking_controller && go test ./... -v

test-dashboard:
cd operator_dashboard && npm test

# === Build ===
build: build-controller build-dashboard

build-controller:
cd tracking_controller && CGO_ENABLED=0 go build -o bin/tracker ./cmd/tracker

build-controller-arm:
cd tracking_controller && CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -o bin/tracker-arm64 ./cmd/tracker

build-dashboard:
cd operator_dashboard && npm run build

# === Docker ===
docker-up:
cd infrastructure && docker-compose -f docker-compose.pi.yml up --build -d

docker-down:
cd infrastructure && docker-compose -f docker-compose.pi.yml down

# === Clean ===
clean:
rm -rf tracking_controller/bin/
rm -rf operator_dashboard/build/
