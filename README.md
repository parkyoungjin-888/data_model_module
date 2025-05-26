# data-model-module

시스템 내부에서 사용하는 data model(pydactic) 공유 및 버전 관리를 위한 모듈

## Index

- [Installation](#installation)
- [History](#History)

## Installation

Instructions for setting up the project.

```bash
# Clone the repository
git clone https://github.com/parkyoungjin-888/common.git

# Install dependencies using Poetry
cd ./common/data_
poetry install
```

## History
+ v0.1.0: init, raw_data_model 추가
+ v0.1.1: validate_decorator 추가
+ v0.1.2: batch 모델 수정, 빌드 파일 제거
+ v0.1.3: 레포 분리, validate_decorator try 문 제거
+ v0.1.4: device_id 추가
+ v0.1.5: images_model 추가
+ v0.1.6: 모델 파일을 minio 에서 관리, 다운로드 및 파일 버전 관리 
+ v0.1.7: 베넷 모듈 제거 테스트
+ v0.1.8: model_importor 를 model_cashe_manager 로 변경
+ v0.1.9: model_file 추가, tool.poetry.exclude 로 설정
+ v0.1.10: 신규 버전 모델로 업데이트 하지 않았던 버그 수정
