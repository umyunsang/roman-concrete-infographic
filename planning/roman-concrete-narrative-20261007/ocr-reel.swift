import Foundation
import Vision
import AppKit

let directory=CommandLine.arguments[1]
let files=try FileManager.default.contentsOfDirectory(atPath:directory).filter{$0.hasPrefix("reel-frame-") && $0.hasSuffix(".jpg")}.sorted()
var results:[[String:Any]]=[]
for (i,name) in files.enumerated() {
    let url=URL(fileURLWithPath:directory).appendingPathComponent(name)
    let request=VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["ko-KR","en-US"]
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(url:url,options:[:]).perform([request])
    let lines=(request.results ?? []).compactMap { obs -> [String:Any]? in
        guard let candidate=obs.topCandidates(1).first else{return nil}
        return ["text":candidate.string,"confidence":candidate.confidence,"box":[obs.boundingBox.minX,obs.boundingBox.minY,obs.boundingBox.width,obs.boundingBox.height]]
    }
    results.append(["frame":name,"time":Double(i)*0.5+0.25,"lines":lines])
}
let data=try JSONSerialization.data(withJSONObject:results,options:[.prettyPrinted,.sortedKeys])
try data.write(to:URL(fileURLWithPath:directory).appendingPathComponent("reel-ocr.json"))
print("OCR frames: \(results.count)")
