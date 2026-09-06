import { BookOpen, Check, ChevronRight } from "lucide-react";

export default function CurriculumRail({ concepts, activeId, completed, onChoose }) {
  let stage = "";
  return (
    <aside className="course-rail">
      <div className="course-heading"><BookOpen size={16} /><div><span className="eyebrow">BEGINNER PATH</span><strong>Neural Networks from Zero</strong></div></div>
      <div className="course-list">
        {concepts.map((concept, index) => {
          const showStage = stage !== concept.stage;
          stage = concept.stage;
          return <div key={concept.id}>
            {showStage && <div className="course-stage">{concept.stage}</div>}
            <button className={concept.id === activeId ? "active" : ""} onClick={() => onChoose(concept.id)}>
              <span className="course-number">{completed.has(concept.id) ? <Check size={12} /> : index + 1}</span>
              <span>{concept.name}</span><ChevronRight size={13} />
            </button>
          </div>;
        })}
      </div>
    </aside>
  );
}
